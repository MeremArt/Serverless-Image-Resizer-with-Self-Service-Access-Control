import json
import boto3
import os
from datetime import datetime
from io import BytesIO
from PIL import Image

# Initialize AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Environment variables
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

IMAGE_SIZES = {
    'thumbnail': (150, 150),
    'medium': (500, 500),
    'large': (1200, 1200)
}

def lambda_handler(event, context):
    """Processes images uploaded to S3"""
    
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        
        print(f"🔄 Processing: {file_key}")
        
        if not file_key.startswith('uploads/'):
            print(f"⏭️  Skipping: {file_key}")
            return {'statusCode': 200, 'body': 'Skipped'}
        
        response = s3.head_object(Bucket=bucket_name, Key=file_key)
        metadata = response.get('Metadata', {})
        user_email = metadata.get('user-email')
        original_filename = metadata.get('original-filename', 'image')
        
        if not user_email:
            print("❌ No user email in metadata")
            return {'statusCode': 400, 'body': 'No email'}
        
        print(f"👤 User: {user_email}")
        
        file_extension = file_key.lower().split('.')[-1]
        
        if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return process_image(bucket_name, file_key, user_email, original_filename)
        else:
            return {'statusCode': 400, 'body': 'Unsupported type'}
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def process_image(bucket_name, file_key, user_email, original_filename):
    """Resize images and send email"""
    
    print(f"📥 Downloading image...")
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    image_data = response['Body'].read()
    
    original_image = Image.open(BytesIO(image_data))
    original_format = original_image.format
    original_size = original_image.size
    
    print(f"📊 Original: {original_size[0]}×{original_size[1]}px, {original_format}")
    
    download_links = {}
    
    print(f"🔧 Resizing...")
    for size_name, dimensions in IMAGE_SIZES.items():
        resized_image = original_image.copy()
        resized_image.thumbnail(dimensions, Image.Resampling.LANCZOS)
        
        output_buffer = BytesIO()
        save_format = 'JPEG'
        resized_image = resized_image.convert('RGB')
        
        resized_image.save(output_buffer, format=save_format, quality=90)
        output_buffer.seek(0)
        
        file_name = file_key.split('/')[-1]
        name_without_ext = '.'.join(file_name.split('.')[:-1])
        output_key = f"processed/{name_without_ext}_{size_name}.jpg"
        
        s3.put_object(
            Bucket=bucket_name,
            Key=output_key,
            Body=output_buffer.getvalue(),
            ContentType='image/jpeg'
        )
        
        download_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': output_key},
            ExpiresIn=604800
        )
        
        download_links[size_name] = download_url
        
        print(f"  ✅ {size_name}: {resized_image.size[0]}×{resized_image.size[1]}px")
    
    print(f"📧 Sending email to {user_email}...")
    email_sent = send_email(user_email, original_filename, download_links)
    
    if email_sent:
        print(f"✅ Complete! Email sent to {user_email}")
    else:
        print(f"⚠️  Processing done but email failed")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Success',
            'email_sent': email_sent
        })
    }


def send_email(user_email, original_filename, download_links):
    """Send email via SNS topic"""
    
    message = f"""Your images are ready! 🎉

Original file: {original_filename}

Download your resized images (links valid for 7 days):

📐 Thumbnail (150x150): 
{download_links['thumbnail']}

📱 Medium (500x500):
{download_links['medium']}

🖼️ Large (1200x1200):
{download_links['large']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ Links expire in 7 days.

Thanks for using Merem Image Resizer!
Powered by AWS • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    
    try:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"✅ Your Resized Images Are Ready - {original_filename}",
            Message=message
        )
        print(f"✅ Email sent via SNS!")
        return True
    except Exception as e:
        print(f"❌ SNS publish failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False