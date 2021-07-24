from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEFAULT_POST_IMG = "../static/img/default-post-img.jpg"

app = Flask(__name__)
app.config["SECRET_KEY"] = "Js4kpytaKqIXow"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog-test.db"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

