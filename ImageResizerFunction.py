import json
import boto3
import os
from PIL import Image
from io import BytesIO
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
sns = boto3.client('sns')

BUCKET_NAME = os.environ.get('BUCKET_NAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

SIZES = {
    'thumbnail': (150, 150),
    'medium': (500, 500),
    'large': (1200, 1200)
}

def lambda_handler(event, context):
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        
        print(f"Processing: s3://{bucket}/{key}")
        
        response = s3.get_object(Bucket=bucket, Key=key)
        image_data = response['Body'].read()
        
        metadata = response.get('Metadata', {})
        user_email = metadata.get('user-email')
        original_filename = metadata.get('original-filename', 'image')
        
        if not user_email:
            print("No user email in metadata, skipping")
            return {'statusCode': 200, 'body': 'No email found'}
        
        print(f"User email: {user_email}")
        
        image = Image.open(BytesIO(image_data))
        
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        download_links = {}
        
        for size_name, dimensions in SIZES.items():
            resized = image.copy()
            resized.thumbnail(dimensions, Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            resized.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            file_name = os.path.basename(key)
            s3_key = f"resized/{size_name}/{file_name}"
            
            s3.put_object(
                Bucket=bucket,
                Key=s3_key,
                Body=buffer.getvalue(),
                ContentType='image/jpeg',
                Metadata=metadata
            )
            
            download_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': s3_key},
                ExpiresIn=604800
            )
            
            download_links[size_name] = download_url
            print(f"Created {size_name}: {s3_key}")
        
        send_email(user_email, original_filename, download_links)
        
        print(f"Successfully processed and sent email to {user_email}")
        
        return {'statusCode': 200, 'body': json.dumps('Success')}
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise


def send_email(email, filename, links):
    message = f"""Your images are ready! 🎉

Original file: {filename}

Download your resized images (links valid for 7 days):

📐 Thumbnail (150x150): 
{links['thumbnail']}

📱 Medium (500x500):
{links['medium']}

🖼️ Large (1200x1200):
{links['large']}

---
Powered by Merem Image Resizer"""
    
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"✅ Your Resized Images Are Ready - {filename}",
        Message=message
    )
    print(f"Email sent to {email}")


