import json
import boto3

# ===== Configuration =====
KNOWLEDGE_BASE_ID = "L2I29PW3Z9"
MODEL_ID = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"
REGION = "ap-northeast-2"

# ===== Clients =====
bedrock_agent = boto3.client('bedrock-agent-runtime', region_name=REGION)

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
    if event.get('httpMethod') == 'OPTIONS':
        return cors_response(200, '')
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '').strip()
        exam_type = body.get('exam', 'SAA-C03')
        lang = body.get('lang', 'ko')
        
        if not user_message:
            return cors_response(400, {'error': '질문을 입력해주세요.' if lang == 'ko' else 'Please enter a question.'})
        
        # Select system prompt based on language
        system_prompt = SYSTEM_PROMPT_EN if lang == 'en' else SYSTEM_PROMPT_KO
        
        response = bedrock_agent.retrieve_and_generate(
            input={'text': user_message},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': KNOWLEDGE_BASE_ID,
                    'modelArn': f'arn:aws:bedrock:{REGION}:797240615245:inference-profile/{MODEL_ID}',
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': system_prompt + "\n\nContext: $search_results$\n\nQuestion: $query$\n\nAnswer:"
                        }
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'filter': {
                                'orAll': [
                                    {'equals': {'key': 'exam', 'value': exam_type}},
                                    {'equals': {'key': 'exam', 'value': 'ALL'}}
                                ]
                            }
                        }
                    }
                }
            }
        )
        
        answer = response['output']['text']
        
        citations = []
        if 'citations' in response:
            for citation in response['citations']:
                for ref in citation.get('retrievedReferences', []):
                    source = ref.get('location', {}).get('s3Location', {}).get('uri', '')
                    text_snippet = ref.get('content', {}).get('text', '')[:200]
                    if source:
                        citations.append({
                            'source': source,
                            'snippet': text_snippet
                        })
        
        return cors_response(200, {
            'answer': answer,
            'citations': citations,
            'exam': exam_type
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return cors_response(500, {'error': '답변 생성 중 오류가 발생했습니다.' if lang == 'ko' else 'An error occurred while generating the answer.'})


def cors_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else body
    }
