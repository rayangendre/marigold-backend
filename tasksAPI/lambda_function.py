import json
import boto3
import tasks
import items

from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table_name = 'Tasks'
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    
    # Extract the HTTP method, path, and request body from the API Gateway event
    print(event)
    http_method = event['httpMethod']
    path = event['path']
    
    

    if path == '/task':
        return tasks.tasks(http_method, event)
    elif path == '/task/items':
        return items.items(http_method, event)
        
        
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Unsupported path or resource')
    }


def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)