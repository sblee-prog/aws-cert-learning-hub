import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CertHub-WebSocket-Connections')

def lambda_handler(event, context):
    connection_id = event['requestContext']['connectionId']
    table.put_item(Item={'connectionId': connection_id})
    return {'statusCode': 200, 'body': 'Connected'}
