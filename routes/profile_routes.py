from flask import request, redirect, url_for, render_template, Blueprint
from flask_login.utils import login_required, current_user
from config import db
from models import Post, Tag, User
from functions import get_popular_posts, upload_to_s3, update_user
from sqlalchemy import desc

profile_routes = Blueprint("profile_routes", __name__)


@profile_routes.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get(user_id)
    user_posts = (
        Post.query.filter_by(author_id=user_id).order_by(desc(Post.created_date)).all()
    )
    top_posts = get_popular_posts()
    all_tags = Tag.query.all()
    return render_template(
        "profile.html",
        user_id=user_id,
        user=user,
        user_posts=user_posts,
        top_posts=top_posts,
        all_tags=all_tags,
        title=f"Hvizd profil - {user.name}",
    )


@profile_routes.route("/edit-profile/<int:user_id>", methods=["GET", "POST"])
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

        return redirect(url_for("profile_routes.profile", user_id=user_id))

    if current_user.id == user_id:
        hash = current_user.password.split("$")[-1]
        return render_template("edit-profile.html", hash=hash, title="Upraviť profil")
    else:
        return redirect(url_for("home"))


@profile_routes.route("/delete-profile/<int:user_id>")
@login_required
def delete_profile(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("home"))
