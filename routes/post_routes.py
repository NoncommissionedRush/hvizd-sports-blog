from flask import request, redirect, url_for, render_template, Blueprint
from flask_login.utils import login_required, current_user
from config import db
from models import Post, Tag
from functions import update_post, kebab, get_popular_posts

post_routes = Blueprint("post_routes", __name__)


@post_routes.route("/post/<int:post_id>/<post_title>")
def post(post_id, **kwargs):
    top_posts = get_popular_posts()
    all_tags = Tag.query.all()
    post = Post.query.get(post_id)

    # increase post view count by one
    if kwargs.get("post_title") == kebab(post.title):
        post.views += 1
        db.session.add(post)
        db.session.commit()

    return render_template(
        "post.html",
        post=post,
        top_posts=top_posts,
        all_tags=all_tags,
        title=f"{post.title}",
    )


@post_routes.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        post_title = request.form["post-title"]
        title_img = request.form["title-img"] if request.form["title-img"] else None
        post_body = request.form.get("ckeditor")
        post_tags = request.form.get("post-tags")

        new_post = Post(
            title=post_title,
            title_img=title_img,
            body=post_body,
            author=current_user,
        )

        for tag in post_tags.split(","):
            tag = tag.strip()
            existing_tag = Tag.query.filter_by(name=tag).first()

            if existing_tag:
                new_post.tags.extend([existing_tag])
            elif tag != "":
                new_tag = Tag(name=tag)
                new_post.tags.extend([new_tag])

        db.session.add(new_post)
        db.session.commit()
        return redirect(
            url_for(
                "post_routes.post",
                post_id=new_post.id,
                post_title=kebab(new_post.title),
            )
        )
    return render_template("create-post.html", title="Nový post")


@post_routes.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post_to_edit = Post.query.get(post_id)
    tags_list = [tag.name for tag in post_to_edit.tags]
    tags_string = ", ".join(tags_list)

    if request.method == "POST":
        new_title = request.form["post-title"]
        new_title_img = request.form["title-img"]
        new_body = request.form.get("ckeditor")
        new_tags = request.form["post-tags"]

        update_post(
            post_id,
            tags=new_tags,
            title=new_title,
            title_img=new_title_img,
            body=new_body,
        )

        return redirect(
            url_for(
                "post_routes.post",
                post_id=post_to_edit.id,
                post_title=kebab(post_to_edit.title),
            )
        )
    return render_template(
        "create-post.html",
        is_edit=True,
        post_to_edit=post_to_edit,
        tags_string=tags_string,
        title="Upraviť post",
    )


@post_routes.route("/delete-post/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get(post_id)
    for tag in post_to_delete.tags:
        post_to_delete.tags.remove(tag)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("profile_routes.profile", user_id=post_to_delete.author.id))
