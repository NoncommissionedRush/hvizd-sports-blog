from flask ***REMOVED***quest, flash, url_for, abort
from flask.templating ***REMOVED***nder_template
from flask_login.login_manager import LoginManager
from flask_login.utils import login_required, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils ***REMOVED***direct
from functions import (
    is_safe_url,
    validate,
    update_user,
    update_post,
    get_popular_posts,
    save_img, 
    kebab
)
from config import DEFAULT_POST_IMG, app, db
***REMOVED***, Comment

db.create_all()

# ---------------------------------- LOGIN MANAGER ------------------------------------
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ------------------------------------ ROUTES -------------------------------------------
@app.route("/")
def home():
    all_posts = Post.query.all()
    top_posts = get_popular_posts()
    return render_template("blog.html", all_posts=all_posts, top_posts=top_posts)


# @app.route("/fans")
# def fans():
#     all_users = User.query.all()
#     return render_template("fans.html", all_users=all_users)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

    ***REMOVED***

        if bool(existing_user) and check_password_hash(
            existing_user.password, password
    ***REMOVED***:
            login_user(existing_user)
***REMOVED*** redirect(url_for("home"))
    ***REMOVED***
            flash("Nesprávne prihlasovacie údaje")
***REMOVED*** redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hash_string = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
    ***REMOVED***
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
            new_user = User(name=name, email=email, password=hash_string)
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
        name = request.form["name"]
        fav_team = request.form["fav-team"]
        hometown = request.form["hometown"]
        about = request.form["about"]
        facebook = request.form["facebook"]
        twitter = request.form["twitter"]
        instagram = request.form["instagram"]
        file = request.files["file"]
        profile_img = current_user.profile_img

        profile_img = save_img(file, profile_img)

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



@app.route("/delete-profile/<int:user_id>")
@login_required
def delete_profile(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
***REMOVED***
    return redirect(url_for("home"))


@app.route("/post/<int:post_id>/title/<post_title>")
def post(post_id, **kwargs):
    top_posts = get_popular_posts()
    post = Post.query.get(post_id)
    # increase post view count by one
    post.views += 1
    db.session.add(post)
***REMOVED***
    return render_template("post.html", post=post, top_posts=top_posts)


@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_title = request.form["post-title"]
        title_img = request.form["title-img"] if request.form["title-img"] else None
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
        new_title_img = request.form["title-img"] if request.form["title-img"] else DEFAULT_POST_IMG
        new_body = request.form.get("ckeditor")

        update_post(post_id, title=new_title, title_img=new_title_img, body=new_body)
        return redirect(url_for("post", post_id=post_to_edit.id))
    return render_template(
        "create-post.html",
        is_edit=True,
        post_to_edit=post_to_edit
***REMOVED***


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
    post = Post.query.get(post_id)
    if request.method == "POST":
        comment_body = request.form["comment"]
        new_comment = Comment(
            body=comment_body, author=current_user, post=post
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
