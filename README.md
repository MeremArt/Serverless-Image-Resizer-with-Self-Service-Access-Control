# Serverless-Image-Resizer-with-Self-Service-Access-Control

### Architecture Overview

https://www.figma.com/board/WGoYrsUaPJOoCgky1DZEZ9/peertopair?node-id=0-1&t=f8ZdcVjI7Qgzutlc-1

### Features

🔐 Self-Service Access Control , you request access, verify email, and get instant approval

📤 Simple Upload Interface - Drag-and-drop or click to upload images
🖼️ Automatic Resizing - Generates 3 optimized sizes(for free!)

Thumbnail: 150×150px
Medium: 500×500px
Large: 1200×1200px

Email Delivery - Download links sent automatically via AWS SNS
Event-Driven Processing - S3 triggers Lambda on upload
Whitelist Security - Only verified emails can upload
Cost-Effective - Pay only for what you use (~$0.05 per 100 images)
Scalable - Handles 1 user or 1 million users automatically

## Installation

Prerequisites

AWS Account
AWS CLI configured with credentials
Python 3.9+
Basic knowledge of AWS services

# Clone Repository

```
 git clone https://github.com/meremart/serverless-image-resizer.git
    cd serverless-image-resizer
```

## Configuration

| **Lambda Function**      | **Variable**    | **Description**       | **Example**       |
| ------------------------ | --------------- | --------------------- | ----------------- |
| **ImageUploadHandler**   | `BUCKET_NAME`   | S3 bucket for uploads | `my-image-bucket` |
|                          | `SNS_TOPIC_ARN` | SNS topic ARN         | `arn:aws:sns:...` |
| **RequestAccessHandler** | `SNS_TOPIC_ARN` | SNS topic ARN         | `arn:aws:sns:...` |
| **ProcessS3Data**        | `BUCKET_NAME`   | S3 bucket name        | `my-image-bucket` |
|                          | `SNS_TOPIC_ARN` | SNS topic ARN         | `arn:aws:sns:...` |

## IAM Permissions Required

Each Lambda function needs:

```{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish",
        "sns:Subscribe",
        "sns:ListSubscriptionsByTopic"
      ],
      "Resource": "arn:aws:sns:*:*:ImageResizerNotifications"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}

```

## Cost Breakdown

| **Service**       | **Usage**                           | **Cost**         |
| ----------------- | ----------------------------------- | ---------------- |
| **Lambda**        | 3,000 invocations, 512 MB, avg 2 s  | ~$0.10           |
| **S3**            | 10 GB storage, 3,000 PUT, 3,000 GET | ~$0.50           |
| **SNS**           | 1,000 email notifications           | ~$0.20           |
| **API Gateway**   | 2,000 requests                      | ~$0.01           |
| **Data Transfer** | 5 GB outbound                       | ~$0.45           |
| **Total**         | —                                   | **~$1.26/month** |

Idle Cost: $0.00 (only pay for usage)
Free Tier Benefits:

Lambda: 1M free requests/month + 400,000 GB-seconds
S3: 5GB storage + 20,000 GET + 2,000 PUT
SNS: 1,000 email notifications free
API Gateway: 1M requests free (first 12 months)

Made with ❤️ and ☕ using AWS Serverless by merem
