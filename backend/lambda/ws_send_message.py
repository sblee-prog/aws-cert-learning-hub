import json
import boto3
import os

# ===== Configuration =====
KNOWLEDGE_BASE_ID = "L2I29PW3Z9"
MODEL_ID = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
REGION = "ap-northeast-2"

# ===== Clients =====
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=REGION)
bedrock_runtime = boto3.client('bedrock-runtime', region_name=REGION)

# ===== System Prompts =====
SYSTEM_PROMPT_KO = """당신은 AWS 자격증 학습을 돕는 AI Tutor입니다.

규칙:
1. 항상 한국어로 답변하세요.
2. AWS 공식 문서를 근거로 정확하게 설명하세요.
3. 검색된 문서(context)에 없는 내용은 추측하지 말고 "해당 내용은 제공된 자료에서 찾을 수 없습니다"라고 답하세요.
4. 시험 문제에 대한 질문이면 정답, 정답인 이유, 오답인 이유를 설명하세요.
5. 개념 질문이면 쉬운 비유와 실제 사용 사례를 포함해서 설명하세요.
6. 답변 마지막에 관련된 AWS 서비스나 추가 학습 키워드를 제안하세요.
"""

SYSTEM_PROMPT_EN = """You are an AI Tutor helping users prepare for AWS certifications.

Rules:
1. Always respond in English.
2. Explain accurately based on official AWS documentation.
3. If the information is not in the provided context, say "This information is not available in the provided materials."
4. For exam questions: explain the correct answer, why it's correct, and why other options are wrong.
5. For concept questions: include simple analogies and real-world use cases.
6. At the end, suggest related AWS services or additional study keywords.
"""


def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    domain = event['requestContext']['domainName']
    stage = event['requestContext']['stage']
    
    endpoint_url = f"https://{domain}/{stage}"
    apigw = boto3.client('apigatewaymanagementapi', endpoint_url=endpoint_url)
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '').strip()
        exam_type = body.get('exam', 'SAA-C03')
        lang = body.get('lang', 'ko')
        
        if not user_message:
            send_to_client(apigw, connection_id, {
                'type': 'error',
                'content': '질문을 입력해주세요.' if lang == 'ko' else 'Please enter a question.'
            })
            return {'statusCode': 200}
        
        # Step 1: Retrieve relevant documents from Knowledge Base
        retrieve_response = bedrock_agent.retrieve(
            knowledgeBaseId=KNOWLEDGE_BASE_ID,
            retrievalQuery={'text': user_message},
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': 5,
                    'filter': {
                        'orAll': [
                            {'equals': {'key': 'exam', 'value': exam_type}},
                            {'equals': {'key': 'exam', 'value': 'ALL'}}
                        ]
                    }
                }
            }
        )
        
        # Build context from retrieved documents
        context_chunks = []
        citations = []
        for result in retrieve_response.get('retrievalResults', []):
            text = result.get('content', {}).get('text', '')
            source = result.get('location', {}).get('s3Location', {}).get('uri', '')
            if text:
                context_chunks.append(text)
            if source:
                citations.append(source)
        
        context = "\n\n".join(context_chunks[:5])
        
        # Step 2: Select system prompt
        system_prompt = SYSTEM_PROMPT_EN if lang == 'en' else SYSTEM_PROMPT_KO
        
        # Step 3: Stream response from Claude
        full_prompt = f"{system_prompt}\n\nContext from AWS documentation:\n{context}\n\nQuestion: {user_message}\n\nAnswer:"
        
        # Send start signal
        send_to_client(apigw, connection_id, {'type': 'stream_start'})
        
        # Invoke model with streaming
        response = bedrock_runtime.invoke_model_with_response_stream(
            modelId=MODEL_ID,
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [
                    {'role': 'user', 'content': full_prompt}
                ]
            })
        )
        
        # Stream tokens to client
        stream = response.get('body')
        for event_obj in stream:
            chunk = event_obj.get('chunk')
            if chunk:
                chunk_data = json.loads(chunk.get('bytes').decode())
                
                if chunk_data.get('type') == 'content_block_delta':
                    delta = chunk_data.get('delta', {})
                    if delta.get('type') == 'text_delta':
                        text = delta.get('text', '')
                        if text:
                            send_to_client(apigw, connection_id, {
                                'type': 'stream_chunk',
                                'content': text
                            })
        
        # Send end signal with citations
        send_to_client(apigw, connection_id, {
            'type': 'stream_end',
            'citations': list(set(citations))
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        try:
            send_to_client(apigw, connection_id, {
                'type': 'error',
                'content': '답변 생성 중 오류가 발생했습니다.' if lang == 'ko' else 'An error occurred while generating the answer.'
            })
        except:
            pass
    
    return {'statusCode': 200}


def send_to_client(apigw, connection_id, data):
    apigw.post_to_connection(
        ConnectionId=connection_id,
        Data=json.dumps(data, ensure_ascii=False).encode('utf-8')
    )
