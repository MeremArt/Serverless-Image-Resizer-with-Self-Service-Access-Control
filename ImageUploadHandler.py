import json
import boto3
import base64
import uuid
import os
from datetime import datetime

s3 = boto3.client('s3')
sns = boto3.client('sns')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:ca-central-1:766957562446:DataPipelineNotifications')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        body = json.loads(event.get('body', '{}'))
        user_email = body.get('email')
        image_data = body.get('image')
        file_name = body.get('fileName', 'image.jpg')
        
        print(f"Upload request from: {user_email}")
        
        if not user_email or not image_data:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Missing email or image'})
            }
        
        # CHECK IF USER IS WHITELISTED
        print(f"Checking whitelist for: {user_email}")
        whitelist_result = is_whitelisted(user_email)
        print(f"Whitelist check result: {whitelist_result}")
        
        if not whitelist_result:
            print(f"Email {user_email} not approved")
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Email not approved',
                    'message': 'Your email is not on the approved list. Please request access first.',
                    'action': 'join_waitlist'
                })
            }
        
        print(f"Email {user_email} is approved, proceeding with upload")
        
        file_extension = file_name.split('.')[-1].lower()
        if file_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid file type'})
            }
        
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        s3_key = f"uploads/{timestamp}-{unique_id}.{file_extension}"
        
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        if len(image_bytes) > 10 * 1024 * 1024:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'File too large'})
            }
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_bytes,
            ContentType=f'image/{file_extension}',
            Metadata={
                'user-email': user_email,
                'original-filename': file_name,
                'upload-timestamp': timestamp
            }
        )
        
        print(f"Successfully uploaded {s3_key} for {user_email}")
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'message': 'Upload successful!',
                'uploadId': unique_id
            })
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }


def is_whitelisted(email):
    """Check if email is subscribed to SNS topic"""
    try:
        print(f"Starting whitelist check for {email}")
        print(f"SNS Topic ARN: {SNS_TOPIC_ARN}")
        
        if not SNS_TOPIC_ARN:
            print("ERROR: SNS_TOPIC_ARN environment variable not set!")
            return False
        
        paginator = sns.get_paginator('list_subscriptions_by_topic')
        
        for page in paginator.paginate(TopicArn=SNS_TOPIC_ARN):
            print(f"Checking page with {len(page['Subscriptions'])} subscriptions")
            
            for subscription in page['Subscriptions']:
                sub_email = subscription.get('Endpoint', '')
                sub_arn = subscription.get('SubscriptionArn', '')
                
                print(f"Checking subscription: {sub_email} - ARN: {sub_arn}")
                
                if sub_email.lower() == email.lower():
                    if sub_arn == 'PendingConfirmation':
                        print(f"Found {email} but pending confirmation")
                        return False
                    else:
                        print(f"Found {email} and confirmed!")
                        return True
        
        print(f"Email {email} not found in subscriptions")
        return False
        
    except Exception as e:
        print(f"Error in is_whitelisted: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False