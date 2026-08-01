import boto3
import json
import subprocess

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('CertHub-Questions-SAA-C03')

response = table.scan()
items = response['Items']

while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    items.extend(response['Items'])

print(f"Total items: {len(items)}")

# RAG용 텍스트 파일로 변환
with open('saa-questions-rag.txt', 'w', encoding='utf-8') as f:
    count = 0
    for item in items:
        if not item.get('answer_letter'):
            continue
        f.write(f"=== Question {item['question_id']} ===\n")
        f.write(f"Domain: {item.get('domain', 'N/A')}\n")
        f.write(f"Question: {item.get('question_text', '')}\n")
        if item.get('options'):
            for opt in item['options']:
                f.write(f"  {opt}\n")
        f.write(f"Correct Answer: {item.get('answer_letter', '')}\n")
        f.write(f"Explanation: {item.get('explanation', '')}\n\n")
        count += 1

print(f"Questions with answers: {count}")
print("Saved to saa-questions-rag.txt")

subprocess.run(['aws', 's3', 'cp', 'saa-questions-rag.txt',
                's3://cert-hub-knowledge/questions/saa-questions-rag.txt'])
print("Uploaded to S3!")
