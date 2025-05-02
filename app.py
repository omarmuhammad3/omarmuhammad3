from flask import Flask, render_template, flash # type: ignore
from flask_wtf import FlaskForm # type: ignore
from wtforms import FileField, SubmitField # type: ignore
from werkzeug.utils import secure_filename # type: ignore
from wtforms.validators import InputRequired # type: ignore
import boto3 # type: ignore
from botocore.exceptions import NoCredentialsError # type: ignore
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YourSecretKey123'

# S3 Configuration
S3_BUCKET = "visca-barca-s3  "  # Replace with your bucket name
S3_REGION = "eu-north-1"  # Change region if needed
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'txt'}

s3 = boto3.client('s3', region_name=S3_REGION)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, bucket_name):
    try:
        filename = secure_filename(file.filename)
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        return f"https://{bucket_name}.s3.{S3_REGION}.amazonaws.com/{filename}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload")

@app.route('/', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            download_url = upload_to_s3(file, S3_BUCKET)
            if download_url:
                flash(f'Success! <a href="{download_url}" target="_blank">Download Link</a>', 'success')
            else:
                flash('Upload failed', 'danger')
    return render_template('upload.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)