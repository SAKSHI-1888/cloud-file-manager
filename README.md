# Cloud File Manager

A Python application for managing objects in a private Amazon S3 bucket using Boto3 and Streamlit.

## Features

- Upload files to an S3 bucket
- List objects and inspect file sizes
- Generate time-limited presigned download URLs
- Delete objects from the bucket
- Use the standard AWS credential provider chain; no credentials are stored in source code

## Requirements

- Python 3.10+
- An AWS account and an S3 bucket
- AWS credentials configured through an IAM role, environment, or AWS CLI profile

## Setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `S3_BUCKET_NAME` to your bucket name, then run:

```bash
streamlit run app.py
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## Security

Use least-privilege IAM permissions. Never commit AWS access keys, secret keys, session tokens, or `.env` files. Presigned URLs grant temporary access to the specified object.

## Scope

This is an educational portfolio project. Review IAM permissions and bucket policies before using it with important data.
