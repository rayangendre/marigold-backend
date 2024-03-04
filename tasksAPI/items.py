import json
import boto3
import library

dynamodb = boto3.resource('dynamodb')
table_name = 'Tasks'
table = dynamodb.Table(table_name)


def items(http_method, event):
    if http_method == "POST":
        request_body = json.loads(event['body']) if 'body' in event else None
        if request_body:
            if 'queryStringParameters' in event:
                query_parameters = event['queryStringParameters']
                user_id = query_parameters['user_id']
                task_id = query_parameters['task_id']
                
                existing_tasks = table.get_item(Key={'user_id': user_id, 'task_id': task_id})
                if 'Item' in existing_tasks:
                    existing_tasks = existing_tasks['Item'].get('tasks', [])
                else:
                    existing_tasks = []
                    
                new_tasks = request_body.get('tasks', [])

                # Check if the order already exists in existing tasks
                existing_orders = set(task.get('order') for task in existing_tasks)
                for task in new_tasks:
                    if 'order' in task and task['order'] in existing_orders:
                        return {
                            'statusCode': 400, 
                            'body': json.dumps({'message': f"Order {task['order']} already exists for the user."})
                        }
                
                update_expression = "SET tasks = list_append(if_not_exists(tasks, :empty_list), :task)"
                expression_attribute_values = {
                    ':task': new_tasks,
                    ':empty_list': []
                }
                response = table.update_item(
                    Key={'user_id': user_id, 'task_id': task_id},
                    UpdateExpression=update_expression,
                    ExpressionAttributeValues=expression_attribute_values
                )
                
                return {
                    'statusCode' : 200,
                    'body' : json.dumps("Order Added")
                }
                
        

            return {
                'statusCode': 400,
                'body': json.dumps("Did not include query parameters")
    
            }
    elif http_method == "GET":
        if "queryStringParameters" in event:
            query_parameters = event["queryStringParameters"]
            if query_parameters is not None and "user_id" in query_parameters and "task_id" in query_parameters and "order" in query_parameters:
                user_id = query_parameters["user_id"]
                task_id = query_parameters["task_id"]
                order = int(query_parameters["order"])

                # Retrieve tasks for the user
                response = table.get_item(Key={'user_id': user_id, 'task_id': task_id})
                item = response.get("Item")
                if item:
                    tasks = item.get("tasks", [])
                    for task in tasks:
                        if task.get("order") == order:
                            return {
                                "statusCode": 200,
                                "body": json.dumps(task, default=library.default)
                            }
                    return {
                        "statusCode": 404,
                        "body": json.dumps(f"Task with order {order} not found for user {user_id}")
                    }
                else:
                    return {
                        "statusCode": 404,
                        "body": json.dumps(f"No tasks found for user {user_id}")
                    }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps("Both user_id and order are required in query parameters for GET")
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps("No query parameters provided for GET")
            }

    elif http_method == "DELETE":
        if "queryStringParameters" in event:
            query_parameters = event["queryStringParameters"]
            if query_parameters is not None and "user_id" in query_parameters and "task_id" in query_parameters and "order" in query_parameters:
                user_id = query_parameters["user_id"]
                task_id = query_parameters["task_id"]
                order = int(query_parameters["order"])

                # Retrieve tasks for the user
                response = table.get_item(Key={'user_id': user_id, 'task_id': task_id})
                item = response.get("Item")
                if item:
                    tasks = item.get("tasks", [])
                    updated_tasks = [task for task in tasks if task.get("order") != order]
                    table.update_item(
                        Key={'user_id': user_id, 'task_id': task_id},
                        UpdateExpression="SET tasks = :tasks",
                        ExpressionAttributeValues={":tasks": updated_tasks}
                    )
                    return {
                        "statusCode": 200,
                        "body": json.dumps(f"Task with order {order} deleted successfully for user {user_id}")
                    }
                else:
                    return {
                        "statusCode": 404,
                        "body": json.dumps(f"No tasks found for user {user_id}")
                    }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps("Both user_id and order are required in query parameters for DELETE")
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps("No query parameters provided for DELETE")
            }

    elif http_method == "PATCH":
        if "queryStringParameters" in event:
            query_parameters = event["queryStringParameters"]
            if query_parameters is not None and "user_id" in query_parameters and "task_id" in query_parameters and "order" in query_parameters:
                user_id = query_parameters["user_id"]
                task_id = query_parameters["task_id"]
                order = int(query_parameters["order"])

                # Extract updated task details from request body
                request_body = json.loads(event["body"]) if "body" in event else None
                if request_body:
                    # Retrieve tasks for the user
                    response = table.get_item(Key={'user_id': user_id, 'task_id': task_id})
                    item = response.get("Item")
                    if item:
                        tasks = item.get("tasks", [])
                        for task in tasks:
                            if task.get("order") == order:
                                # Update the task with new details
                                task.update(request_body)
                                table.update_item(
                                    Key={'user_id': user_id, 'task_id': task_id},
                                    UpdateExpression="SET tasks = :tasks",
                                    ExpressionAttributeValues={":tasks": tasks}
                                )
                                return {
                                    "statusCode": 200,
                                    "body": json.dumps(f"Task with order {order} updated successfully for user {user_id}")
                                }
                        return {
                            "statusCode": 404,
                            "body": json.dumps(f"Task with order {order} not found for user {user_id}")
                        }
                    else:
                        return {
                            "statusCode": 404,
                            "body": json.dumps(f"No tasks found for user {user_id}")
                        }
                else:
                    return {
                        "statusCode": 400,
                        "body": json.dumps("Invalid request body for PATCH")
                    }
            else:
                return {
                    "statusCode": 400,
                    "body": json.dumps("Both user_id and order are required in query parameters for PATCH")
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps("No query parameters provided for PATCH")
            }

    else:
        return {
            "statusCode": 405,
            "body": json.dumps("Unsupported method")
        }
