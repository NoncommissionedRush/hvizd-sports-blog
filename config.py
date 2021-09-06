from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_migrate import Migrate
import os

UPLOAD_FOLDER = "./static/img"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
DEFAULT_POST_IMG = "default-post-img.jpg"
DEFAULT_PROFILE_IMG = "default-profile-img.jpeg"
POSTS_PER_PAGE = 10

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
S3_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_ACCESS_KEY")
S3_LOCATION = f"http://{S3_BUCKET}.s3.amazonaws.com/"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///blog.db"
)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.jinja_env.globals.update(default_post_img=DEFAULT_POST_IMG)
app.jinja_env.globals.update(default_profile_img=DEFAULT_PROFILE_IMG)
app.jinja_env.globals.update(posts_per_page=POSTS_PER_PAGE)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)
