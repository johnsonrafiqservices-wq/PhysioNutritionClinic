"""
Cloudflare R2 PDF storage utility.

Uploads PDFs to Cloudflare R2 (S3-compatible) and returns a public
download URL that works from any device — no Django server needed.
"""
import logging

import boto3
from botocore.config import Config
from django.conf import settings

logger = logging.getLogger(__name__)

_s3_client = None


def _get_s3_client():
    """Lazy-initialise and cache the boto3 S3 client for Cloudflare R2."""
    global _s3_client
    if _s3_client is not None:
        return _s3_client

    _s3_client = boto3.client(
        's3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )
    return _s3_client


def upload_pdf_to_drive(pdf_bytes, filename, subfolder='documents'):
    """
    Upload a PDF to Cloudflare R2 and return a public download URL.

    Args:
        pdf_bytes: raw bytes of the PDF file
        filename: desired filename (e.g. 'Joyce_Akello_invoice_INV001.pdf')
        subfolder: folder prefix ('invoices', 'receipts', 'certificates', 'reports')

    Returns:
        str: public download URL
    """
    client = _get_s3_client()
    bucket = settings.R2_BUCKET_NAME
    key = f'{subfolder}/{filename}'

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=pdf_bytes,
        ContentType='application/pdf',
    )

    # Build public URL
    public_base = getattr(settings, 'R2_PUBLIC_URL', '').rstrip('/')
    if public_base:
        download_url = f'{public_base}/{key}'
    else:
        # Fallback: generate a pre-signed URL valid for 7 days
        download_url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=604800,  # 7 days
        )

    logger.info('Uploaded %s (%d bytes) to R2 → %s', filename, len(pdf_bytes), download_url)
    return download_url


def get_pdf_from_r2(subfolder, filename):
    """
    Retrieve a PDF from Cloudflare R2.

    Returns:
        bytes: raw PDF content, or None if not found.
    """
    client = _get_s3_client()
    bucket = settings.R2_BUCKET_NAME
    key = f'{subfolder}/{filename}'

    try:
        response = client.get_object(Bucket=bucket, Key=key)
        return response['Body'].read()
    except client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        logger.error('Failed to get %s from R2: %s', key, e)
        return None
