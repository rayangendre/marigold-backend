import json
import boto3

from decimal import Decimal

import library

dynamodb = boto3.resource('dynamodb')
table_name = 'Tasks'
table = dynamodb.Table(table_name)



def tasks(http_method, event):
    if http_method == 'POST':
        request_body = json.loads(event['body']) if 'body' in event else None
        if request_body:
            if 'task_id' not in request_body:
                return {
                'statusCode': 400, 
                'body': json.dumps('task_id is required in the body')
            }
            if 'user_id' not in request_body:
                return {
                'statusCode': 400, 
                'body': json.dumps('task_id is required in the body')
            }
            
            
            table.put_item(Item=request_body)
            return {
                'statusCode': 201,  # 201 Created
                'body': json.dumps('Item successfully created')
            }
        else:
            return {
                'statusCode': 400,  # 400 Bad Request
                'body': json.dumps('Invalid request body')
            }
        
    elif http_method == 'GET':
        if 'queryStringParameters' in event:
            query_parameters = event['queryStringParameters']
            if query_parameters != None and 'user_id' in query_parameters and 'task_id' in query_parameters:
                # Retrieve a specific user by ID
                user_id = query_parameters['user_id']
                task_id = query_parameters['task_id']
                response = table.get_item(Key={'user_id': user_id, 'task_id' : task_id})
                item = response.get('Item')
                if item:
                    return {
                        'statusCode': 200,
                        'body': json.dumps(item, default=library.default)
                    }
                else:
                    return {
                        'statusCode': 404,  # 404 Not Found
                        'body': json.dumps('Tasks not found')
                    }
                    
                    
            elif query_parameters != None and 'user_id' in query_parameters:
                user_id = query_parameters['user_id']
                response = table.query(
                    KeyConditionExpression='user_id = :uid',
                    ExpressionAttributeValues={
                        ':uid': user_id
                    }
                )
                items = response.get('Items', [])
                if items:
                    return {
                        'statusCode': 200,
                        'body': json.dumps(items, default=library.default)
            
                    }
                else:
                    return {
                        'statusCode': 404,  # 404 Not Found
                        'body': json.dumps('Tasks for ' + user_id + ' not found')
                    }
            return {
                'statusCode': 404,
                'body': json.dumps("Did not include query parameters")
    
            }
    elif http_method == 'DELETE':
        if 'queryStringParameters' in event:
            query_parameters = event['queryStringParameters']
            if query_parameters != None and 'user_id' in query_parameters and 'task_id' in query_parameters:
                # Delete a specific task
                user_id = query_parameters['user_id']
                task_id = query_parameters['task_id']
                response = table.delete_item(Key={'user_id': user_id, 'task_id': task_id})
                return {
                    'statusCode': 200,  
                    'body': json.dumps('Task deleted successfully')
                }
            else:
                return {
                    'statusCode': 400,  # 400 Bad Request
                    'body': json.dumps('Both user_id and task_id are required in query parameters for DELETE')
                }
        else:
            return {
                'statusCode': 400,  # 400 Bad Request
                'body': json.dumps('No query parameters provided for DELETE')
            }
    elif http_method == 'PATCH':
        if 'queryStringParameters' in event:
            query_parameters = event['queryStringParameters']
            if query_parameters is not None and 'user_id' in query_parameters and 'task_id' in query_parameters:
                # Update a specific task
                user_id = query_parameters['user_id']
                task_id = query_parameters['task_id']
                
                # Extract updated task details from request body
                request_body = json.loads(event['body']) if 'body' in event else None
                if request_body:
                    update_expression = "SET "
                    expression_attribute_values = {}
                    update_expression_values = []

                    # Construct update expression dynamically based on request body
                    for key, value in request_body.items():
                        update_expression_values.append(f"{key} = :{key}")
                        expression_attribute_values[f":{key}"] = value

                    update_expression += ", ".join(update_expression_values)

                    # Perform the update operation
                    response = table.update_item(
                        Key={'user_id': user_id, 'task_id': task_id},
                        UpdateExpression=update_expression,
                        ExpressionAttributeValues=expression_attribute_values
                    )
                    return {
                        'statusCode': 200,
                        'body': json.dumps('Task updated successfully')
                    }
                else:
                    return {
                        'statusCode': 400,  # 400 Bad Request
                        'body': json.dumps('Invalid request body')
                    }
            else:
                return {
                    'statusCode': 400,  # 400 Bad Request
                    'body': json.dumps('Both user_id and task_id are required in query parameters for PATCH')
                }
        else:
            return {
                'statusCode': 400,  # 400 Bad Request
                'body': json.dumps('No query parameters provided for PATCH')
            }
    else:
        return {
            'statusCode': 405,  # 405 Method Not Allowed
            'body': json.dumps('Unsupported method')
        }