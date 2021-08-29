from flask import request, flash, url_for, abort, jsonify
from flask.templating import render_template
from flask_login.login_manager import LoginManager
from flask_login.utils import login_required, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect
from functions import (
    is_safe_url,
    upload_to_s3,
    validate,
    update_user,
    update_post,
    get_popular_posts,
    kebab,
    send_password_reset_link,
)
from config import app, db, POSTS_PER_PAGE
from models import User, Post, Comment
from sqlalchemy import desc

db.create_all()

# ---------------------------------- LOGIN MANAGER ------------------------------------
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ------------------------------------ ROUTES -------------------------------------------
@app.route("/")
def home():
    all_posts = Post.query.filter().order_by(desc(Post.created_date)).all()
    top_posts = get_popular_posts()
    return render_template("blog.html", all_posts=all_posts, top_posts=top_posts, start=0, end=POSTS_PER_PAGE, page=1, title="Hvizd | Blog")


@app.route("/page/<int:page_nr>")
def page(page_nr):
    start = (page_nr * POSTS_PER_PAGE) - POSTS_PER_PAGE
    end = page_nr * POSTS_PER_PAGE
    all_posts = Post.query.filter().order_by(desc(Post.created_date)).all()
    top_posts = get_popular_posts()
    print(len(all_posts[start:end + 1]) == POSTS_PER_PAGE + 1)
    return render_template("blog.html", all_posts=all_posts, top_posts=top_posts, start=start, end=end, page=page_nr, title="Hvizd | Blog")

# @app.route("/fans")
# def fans():
#     all_users = User.query.all()
#     return render_template("fans.html", all_users=all_users, title="Ľudia")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if bool(existing_user) and check_password_hash(
            existing_user.password, password
        ):
            login_user(existing_user)
            return redirect(url_for("home"))
        else:
            flash("Nesprávne prihlasovacie údaje")
            return redirect(url_for("login"))

    return render_template("login.html", title="Prihlásenie")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hash_string = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        confirm_password = request.form["confirm-password"]

        try:
            validate(email, password, confirm_password)
        except UserWarning as error:
            flash(str(error))
            return redirect(url_for("register"))
        except ValueError as error:
            flash(str(error))
            return redirect(url_for("register"))
        else:
            new_user = User(name=name, email=email, password=hash_string)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            # insurance against open redirects
            next = request.args.get("next")
            if not is_safe_url(next):
                return abort(400)

            return redirect(url_for("home"))

    return render_template("register.html", title="Registrácia")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/password-reset-request", methods=["GET", "POST"])
def password_reset_request():
    if request.method == "POST":
        email = request.form["email"]
        print(f"email je {email}")
        user = User.query.filter_by(email=email).first()
        send_password_reset_link(user)
        return redirect(url_for("login"))

    return render_template("password-reset.html", request=True)


@app.route("/password-reset/<int:user_id>/<string:hash>", methods=["GET", "POST"])
def password_reset(user_id, hash):
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        user = User.query.get(user_id)
        if password == confirm_password:
            update_user(
                user_id,
                password=generate_password_hash(
                    password, method="pbkdf2:sha256", salt_length=8
                ),
            )
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Heslá sa musia zhodovať")
            return redirect(url_for("password_reset", user_id=user_id, hash=hash))
    return render_template(
        "password-reset.html", user_id=user_id, hash=hash, request=False, title="Obnova hesla"
    )


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
        title=f"{user.name}"
    )


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

        profile_img = upload_to_s3(file, profile_img)

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
        )

        return redirect(url_for("profile", user_id=user_id))

    if current_user.id == user_id:
        hash = current_user.password.split("$")[-1]
        return render_template("edit-profile.html", hash=hash, title="Upraviť profil")
    else:
        return redirect(url_for("home"))


@app.route("/delete-profile/<int:user_id>")
@login_required
def delete_profile(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/post/<int:post_id>/<post_title>")
def post(post_id, **kwargs):
    top_posts = get_popular_posts()
    post = Post.query.get(post_id)
    # increase post view count by one
    if kwargs.get('post_title') == kebab(post.title):
        post.views += 1
        db.session.add(post)
        db.session.commit()
    return render_template("post.html", post=post, top_posts=top_posts, title=f"{post.title}")
    

@app.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_title = request.form["post-title"]
        title_img = request.form["title-img"] if request.form["title-img"] else None
        post_body = request.form.get("ckeditor")

        new_post = Post(
            title=post_title, title_img=title_img, body=post_body, author=current_user
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(
            url_for("post", post_id=new_post.id, post_title=kebab(new_post.title))
        )
    return render_template("create-post.html", title="Nový post")


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post_to_edit = Post.query.get(post_id)
    if request.method == "POST":
        new_title = request.form["post-title"]
        new_title_img = (
            request.form["title-img"]
        )
        new_body = request.form.get("ckeditor")

        update_post(post_id, title=new_title, title_img=new_title_img, body=new_body)
        return redirect(
            url_for(
                "post", post_id=post_to_edit.id, post_title=kebab(post_to_edit.title)
            )
        )
    return render_template("create-post.html", is_edit=True, post_to_edit=post_to_edit, title="Upraviť post")


@app.route("/delete-post/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("profile", user_id=post_to_delete.author.id))


@app.route("/add-comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get(post_id)
    if request.method == "POST":
        comment_body = request.form["comment"]
        new_comment = Comment(body=comment_body, author=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("post", post_id=post_id, post_title=kebab(post.title)))


@app.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    parent_post = Post.query.get(comment_to_delete.post_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for("post", post_id=comment_to_delete.post_id, post_title=kebab(parent_post.title)))


@app.route("/getinfo")
@login_required
def get_admin_info():
    if current_user.id == 1:
        all_posts = Post.query.all()
        all_users = User.query.all()
        posts = []
        users = []
        for post in all_posts:
            post_details = {
                "title": post.title,
                "author": post.author.name,
                "views": post.views
            }
            posts.append(post_details)

        for user in all_users:
            user_details = {
                "name": user.name,
                "email": user.email
            }
            users.append(user_details)
        res = {
            'posts': posts,
            'users': users
        }

        return res
    else:
        return redirect("/")
    


if __name__ == "__main__":
    app.run(debug=True)
