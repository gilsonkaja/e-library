from flask import Blueprint, request, jsonify, current_app, url_for
import os, uuid
from config import Config
from pathlib import Path

upload_bp = Blueprint("upload", __name__)

USE_S3 = bool(Config.S3_BUCKET and Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY)

if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route("/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error":"No file field 'file' in multipart"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error":"No filename"}), 400

    ext = Path(f.filename).suffix
    key = f"{int(__import__('time').time()*1000)}-{uuid.uuid4()}{ext}"

    if USE_S3:
        import boto3
        s3 = boto3.client("s3",
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            region_name=Config.AWS_REGION)
        s3.put_object(Bucket=Config.S3_BUCKET, Key=key, Body=f.read(), ContentType=f.mimetype)
        url = f"https://{Config.S3_BUCKET}.s3.{Config.AWS_REGION}.amazonaws.com/{key}"
        return jsonify({"filename": key, "url": url, "storage":"s3"})
    else:
        out = os.path.join(Config.UPLOAD_FOLDER, key)
        f.save(out)
        url = f"/uploads/{key}"
        return jsonify({"filename": key, "url": url, "storage":"local"})
