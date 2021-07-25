from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
***REMOVED***

UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEFAULT_POST_IMG = "default-post-img.jpg"

app = Flask(__name__)
app.config["SECRET_KEY"] = "hovienko"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ckeditor = CKEditor(app)

