from flask import request, redirect, url_for, Blueprint
from flask_login.utils import login_required, current_user
from config import db
from models import Post, Comment
from functions import kebab

comment_routes = Blueprint("comment_routes", __name__)


@comment_routes.route("/add-comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get(post_id)
    if request.method == "POST":
        comment_body = request.form["comment"]
        new_comment = Comment(body=comment_body, author=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(
            url_for("post_routes.post", post_id=post_id, post_title=kebab(post.title))
        )


@comment_routes.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    parent_post = Post.query.get(comment_to_delete.post_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(
        url_for(
            "post_routes.post",
            post_id=comment_to_delete.post_id,
            post_title=kebab(parent_post.title),
        )
    )
