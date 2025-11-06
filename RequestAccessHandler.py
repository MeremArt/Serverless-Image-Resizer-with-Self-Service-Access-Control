import json
import boto3
import os

sns = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    """
    Self-service access request
    Creates SNS subscription which sends confirmation email automatically
    User confirms via email link → immediately whitelisted
    """
    
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
        
        if not user_email or '@' not in user_email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid email address'})
            }
        
        # Check if already subscribed
        status = check_subscription_status(user_email)
        
        if status == 'confirmed':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Your email is already approved! You can upload images now.',
                    'status': 'approved'
                })
            }
        
        if status == 'pending':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Verification email already sent! Check your inbox and click the confirmation link.',
                    'status': 'pending'
                })
            }
        
        # Create new subscription (SNS will send confirmation email automatically)
        try:
            response = sns.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol='email',
                Endpoint=user_email,
                ReturnSubscriptionArn=True
            )
            
            print(f"Created subscription for {user_email}")
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'message': 'Verification email sent! Check your inbox and click the confirmation link. Once confirmed, you can immediately use the service.',
                    'status': 'verification_sent',
                    'email': user_email
                })
            }
            
        except sns.exceptions.InvalidParameterException as e:
            if 'Invalid parameter: Email address' in str(e):
                return {
                    'statusCode': 400,
                    'headers': headers,
                    'body': json.dumps({'error': 'Invalid email format'})
                }
            raise
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Failed to process request'})
        }


def check_subscription_status(email):
    """
    Check if email is subscribed and confirmed
    Returns: 'confirmed', 'pending', or 'not_subscribed'
    """
    try:
        paginator = sns.get_paginator('list_subscriptions_by_topic')
        
        for page in paginator.paginate(TopicArn=SNS_TOPIC_ARN):
            for subscription in page['Subscriptions']:
                if subscription['Endpoint'] == email:
                    if subscription['SubscriptionArn'] == 'PendingConfirmation':
                        return 'pending'
                    else:
                        return 'confirmed'
        
        return 'not_subscribed'
        
    except Exception as e:
        print(f"Error checking subscription: {str(e)}")
        return 'not_subscribed'