# Clone repo

git clone https://github.com/yourusername/serverless-image-resizer.git
cd serverless-image-resizer

# Create virtual environment

python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Install dev dependencies

pip install -r requirements-dev.txt

# Run tests

pytest

# Run linter

pylint lambda/

```

### Guidelines

1. Follow PEP 8 style guide
2. Add unit tests for new features
3. Update documentation
4. Use meaningful commit messages
5. Create feature branches (`feature/your-feature-name`)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **AWS Lambda Layers** - [Klayers](https://github.com/keithrozario/Klayers) for Pillow layer
- **AWS Documentation** - Comprehensive guides and examples
- **Dev Community** - For inspiration and best practices
- **Pillow Library** - Powerful image processing in Python

---

## 📞 Contact

**Your Name** - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

**Project Link:** [https://github.com/yourusername/serverless-image-resizer](https://github.com/yourusername/serverless-image-resizer)

**Live Demo:** [https://your-website-url.com](https://your-website-url.com)

**Blog Post:** [Read the full story](https://your-blog.com/serverless-image-resizer)

---

## 📚 Learn More

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html)
- [Amazon SNS Documentation](https://docs.aws.amazon.com/sns/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

---

<div align="center">

Made with ❤️ and ☕ using AWS Serverless

**[⬆ back to top](#-serverless-image-resizer-with-self-service-access-control)**

</div>

---

## 📁 Project Structure Reference
```

serverless-image-resizer/
│
├── assets/ # Images and videos for README
│ ├── architecture-diagram.png
│ ├── video-thumbnail.png
│ ├── demo-video.mp4
│ ├── screenshot-upload.png
│ ├── screenshot-email.png
│ ├── screenshot-request-access.png
│ └── screenshot-resized.png
│
├── lambda/ # Lambda function code
│ ├── ImageUploadHandler/
│ │ ├── lambda_function.py
│ │ └── requirements.txt
│ ├── RequestAccessHandler/
│ │ ├── lambda_function.py
│ │ └── requirements.txt
│ └── ProcessS3Data/
│ ├── lambda_function.py
│ └── requirements.txt
│
├── frontend/ # Static website
│ ├── index.html
│ ├── styles.css
│ └── script.js
│
├── docs/ # Documentation
│ ├── api-gateway-setup.md
│ ├── troubleshooting.md
│ ├── cost-optimization.md
│ └── security-best-practices.md
│
├── scripts/ # Deployment scripts
│ ├── deploy.sh
│ ├── cleanup.sh
│ └── test.sh
│
├── tests/ # Test files
│ ├── test_upload_handler.py
│ ├── test_access_handler.py
│ ├── test_processor.py
│ └── integration_test.py
│
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
└── requirements-dev.txt
