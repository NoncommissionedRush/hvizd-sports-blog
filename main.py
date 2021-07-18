***REMOVED***
import datetime
***REMOVED***
from flask import Flask, request, flash, url_for, abort
from flask.templating ***REMOVED***nder_template
from flask_login.utils import login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils ***REMOVED***direct, secure_filename
from flask_login import LoginManager, UserMixin
from flask_ckeditor import CKEditor


# ------------------------------- Set up app and db -----------------------------------
UPLOAD_FOLDER = './static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DEFAULT_POST_IMG = "../static/img/default-post-img.jpg"


app = Flask(__name__)
app.config["SECRET_KEY"] = "Js4kpytaKqIXow"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog-test.db"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)
ckeditor = CKEditor(app)


# ---------------------------------- upload file ---------------------------------------
***REMOVED***
***REMOVED***


# ---------------------------- Set up database tables ----------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    profile_img = db.Column(db.String(250), default="default-profile-img.jpeg")
    password = db.Column(db.String(250), nullable=False)
    fav_team = db.Column(db.String(250))
    hometown = db.Column(db.String(250))
    about = db.Column(db.String(550))
    facebook = db.Column(db.String(250))
    twitter = db.Column(db.String(250))
    instagram = db.Column(db.String(250))
    posts = db.relationship("Post", back_populates="author")

    def __repr__(self):
        return "<User %r>" % self.email


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False)
    title_img = db.Column(db.String(250), default=DEFAULT_POST_IMG)
    body = db.Column(db.Text())
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User", back_populates="posts")
    views = db.Column(db.Integer, default=0)
    comments = db.relationship("Comment", back_populates="post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    created_date = db.Column(db.DateTime, default=datetime.datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = db.relationship("User")
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    post = db.relationship("Post", back_populates="comments")


db.create_all()

# --------------------------------- login manager -------------------------------------
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ----------------------------------- SAFE URL ------------------------------------------
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
        raise UserWarning("This Email Is Already Registered")
***REMOVED***
        raise ValueError("The Passwords Do Not Match")
***REMOVED***
***REMOVED***


***REMOVED***

***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***


***REMOVED***

***REMOVED***

***REMOVED***
        setattr(post_to_update, attr, value)
    
***REMOVED***
***REMOVED***


***REMOVED***
***REMOVED***


# ------------------------------------ PRETTY DATE -------------------------------------------

***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
***REMOVED***
    
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***

***REMOVED***
***REMOVED***
***REMOVED*** "just now"
***REMOVED***
***REMOVED*** str(second_diff) + " seconds ago"
***REMOVED***
***REMOVED*** "a minute ago"
***REMOVED***
***REMOVED*** str(second_diff // 60) + " minutes ago"
***REMOVED***
***REMOVED*** "an hour ago"
***REMOVED***
            print(f"second_diff {second_diff}")
***REMOVED*** str(second_diff // 3600) + " hours ago"
***REMOVED***
        return "Yesterday"
***REMOVED***
        return str(day_diff) + " days ago"
***REMOVED***
        return str(day_diff / 7) + " weeks ago"
***REMOVED***
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"

***REMOVED***
***REMOVED***
# ------------------------------------ ROUTES -------------------------------------------


@app.route("/")
def home():
    all_posts = Post.query.all()
    top_posts = get_popular_posts()
    return render_template("blog.html", all_posts=all_posts, top_posts=top_posts)


@app.route("/fans")
def fans():
    all_users = User.query.all()
    return render_template("fans.html", all_users=all_users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

    ***REMOVED***

        if bool(existing_user) and existing_user.password == password:
            login_user(existing_user)
***REMOVED*** redirect(url_for("home"))
    ***REMOVED***
            flash("Invalid Credentials")
***REMOVED*** redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # get data from html table
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]

***REMOVED***
            validate(email, password, confirm_password)
        except UserWarning as error:
            flash(str(error))
***REMOVED*** redirect(url_for("register"))
        except ValueError as error:
            flash(str(error))
***REMOVED*** redirect(url_for("register"))
    ***REMOVED***
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
        ***REMOVED***
            login_user(new_user)

            # insurance against open redirects
            next = request.args.get("next")
            if not is_safe_url(next):
    ***REMOVED*** abort(400)

***REMOVED*** redirect(url_for("profile", user_id=new_user.id))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get(user_id)
    user_posts = Post.query.filter_by(author_id=user_id)
    top_posts = get_popular_posts()
    return render_template(
        "profile.html",
        user_id=user_id,
        user=user,
        user_posts=user_posts,
        top_posts=top_posts,
***REMOVED***


@app.route("/edit-profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_profile(user_id):
    if request.method == "POST" and current_user.id == user_id:
        # get form data
        name = request.form["name"]
        fav_team = request.form["fav-team"]
        hometown = request.form["hometown"]
        about = request.form["about"]
        facebook = request.form["facebook"]
        twitter = request.form["twitter"]
        instagram = request.form["instagram"]
        file = request.files['file']
        profile_img = current_user.profile_img

    ***REMOVED***
    ***REMOVED***
    ***REMOVED***
    ***REMOVED***
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(new_filename)))
            profile_img = new_filename
        

        update_user(
            user_id,
            name=name,
            profile_img=profile_img,
            fav_team=fav_team,
            hometown=hometown,
            about=about,
            facebook=facebook,
            twitter=twitter,
            instagram=instagram,
    ***REMOVED***

        return redirect(url_for("profile", user_id=user_id))

    if current_user.id == user_id:
        return render_template("edit-profile.html")
***REMOVED***
        return redirect(url_for("home"))


@app.route("/post/<int:post_id>")
def post(post_id):
    top_posts = get_popular_posts()
    post = Post.query.get(post_id)
    post.views += 1
    db.session.add(post)
***REMOVED***
    return render_template("post.html", post=post, top_posts=top_posts)


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_title = request.form["post-title"]
        title_img = request.form["title-img"] if request.form['title-img'] else None
        post_body = request.form.get("ckeditor")

        new_post = Post(
            title=post_title, title_img=title_img, body=post_body, author=current_user
    ***REMOVED***

        db.session.add(new_post)
    ***REMOVED***
        return redirect(url_for("profile", user_id=current_user.id))
    return render_template("create-post.html")


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post_to_edit = Post.query.get(post_id)
    if request.method == "POST":
        new_title = request.form["post-title"]
        new_title_img = request.form["title-img"]
        new_body = request.form.get("ckeditor")

        post_to_edit.title = new_title
        if new_title_img:
            post_to_edit.title_img = new_title_img
        post_to_edit.body = new_body
        db.session.add(post_to_edit)
    ***REMOVED***
        return redirect(url_for("post", post_id=post_to_edit.id))
    return render_template("create-post.html", is_edit=True, post_to_edit=post_to_edit, default_post_img=DEFAULT_POST_IMG)


@app.route("/delete-post/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    db.session.delete(post_to_delete)
***REMOVED***
    return redirect(url_for("profile", user_id=post_to_delete.author.id))


@app.route("/add-comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    if request.method == "POST":
        comment_body = request.form["comment"]
        new_comment = Comment(
            body=comment_body, author=current_user, post=Post.query.get(post_id)
    ***REMOVED***
        db.session.add(new_comment)
    ***REMOVED***
        return redirect(url_for("post", post_id=post_id))


@app.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
***REMOVED***
    return redirect(url_for("post", post_id=comment_to_delete.post_id))


if __name__ == "__main__":
    app.run(debug=True)
