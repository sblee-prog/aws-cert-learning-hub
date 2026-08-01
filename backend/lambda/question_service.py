import json
import boto3
import random
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2')
table = dynamodb.Table('CertHub-Questions-SAA-C03')


def lambda_handler(event, context):
    """API Gateway에서 호출되는 메인 핸들러"""
    
    http_method = event.get('httpMethod', '')
    path = event.get('path', '') or event.get('resource', '')
    
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
    }
    
    try:
        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        if http_method == 'GET' and ('questions' in path or 'questions' in event.get('resource', '')):
            return get_questions(event, headers)
        
        elif http_method == 'POST' and ('submit' in path or 'submit' in event.get('resource', '')):
            return submit_answers(event, headers)
        
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def get_questions(event, headers):
    """문제 출제 API"""
    
    params = event.get('queryStringParameters') or {}
    
    mode = params.get('mode', 'random')
    count = int(params.get('count', '10'))
    domain = params.get('domain', '')
    difficulty = params.get('difficulty', '')
    
    # answer_letter가 있는 문제만 필터
    filter_expr = Attr('answer_letter').exists() & Attr('answer_letter').ne('')
    
    if domain:
        filter_expr = filter_expr & Attr('domain').eq(domain)
    if difficulty:
        filter_expr = filter_expr & Attr('difficulty').eq(difficulty)
    
    response = table.scan(FilterExpression=filter_expr)
    items = response['Items']
    
    while 'LastEvaluatedKey' in response:
        response = table.scan(
            FilterExpression=filter_expr,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])
    
    # 랜덤 셔플 후 count개 선택
    random.shuffle(items)
    selected = items[:count]
    
    # 응답 (정답 미포함)
    questions = []
    for q in selected:
        questions.append({
            'question_id': q['question_id'],
            'question': q.get('question_en', ''),
            'options': q.get('options_en', {}),
            'domain': q.get('domain', ''),
            'difficulty': q.get('difficulty', 'medium')
        })
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'questions': questions,
            'total': len(questions),
            'mode': mode
        })
    }


def submit_answers(event, headers):
    """채점 API"""
    
    body = json.loads(event.get('body', '{}'))
    answers = body.get('answers', [])
    
    if not answers:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'No answers provided'})
        }
    
    results = []
    correct_count = 0
    
    for ans in answers:
        question_id = ans.get('question_id', '')
        selected = ans.get('selected', '')
        
        response = table.get_item(Key={'question_id': question_id})
        item = response.get('Item', {})
        
        correct_letter = item.get('answer_letter', '')
        is_correct = (selected.upper() == correct_letter.upper())
        
        if is_correct:
            correct_count += 1
        
        results.append({
            'question_id': question_id,
            'selected': selected,
            'correct': correct_letter,
            'is_correct': is_correct,
            'explanation': item.get('explanation_en', '')
        })
    
    total = len(answers)
    percentage = round((correct_count / total) * 100, 1) if total > 0 else 0
    passed = percentage >= 72.0
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'score': correct_count,
            'total': total,
            'percentage': percentage,
            'passed': passed,
            'passing_threshold': 72.0,
            'results': results
        })
    }
