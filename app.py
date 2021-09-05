from flask import request
from flask_migrate import Migrate
from flask.templating import render_template
from flask_login.login_manager import LoginManager
from flask_login.utils import login_required, current_user
from werkzeug.utils import redirect
from functions import (
    get_popular_posts,
)
from config import app, db, POSTS_PER_PAGE
from models import User, Post
from sqlalchemy import desc

db.create_all()

# ---------------------------------- LOGIN MANAGER ------------------------------------
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# ------------------------------------ ROUTES -------------------------------------------


@app.route("/tag/<string:tag>", defaults={"page_nr": 1})
@app.route("/tag/<string:tag>/page/<int:page_nr>")
@app.route("/page/<int:page_nr>", defaults={"tag": ""})
@app.route("/", defaults={"page_nr": 1, "tag": ""})
def home(page_nr, tag):
    start = (page_nr * POSTS_PER_PAGE) - POSTS_PER_PAGE
    end = page_nr * POSTS_PER_PAGE

    all_posts = Post.query.filter().order_by(desc(Post.created_date)).all()
    top_posts = get_popular_posts()

    print(len(all_posts[start : end + 1]) == POSTS_PER_PAGE + 1)
    return render_template(
        "blog.html",
        all_posts=all_posts,
        top_posts=top_posts,
        start=start,
        end=end,
        page=page_nr,
        title="Hvizd | Blog",
    )


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
                "views": post.views,
            }
            posts.append(post_details)

        for user in all_users:
            user_details = {"name": user.name, "email": user.email}
            users.append(user_details)
        res = {"posts": posts, "users": users}

        return res
    else:
        return redirect("/")


from routes.post_routes import post_routes
from routes.profile_routes import profile_routes
from routes.login_routes import login_routes
from routes.comment_routes import comment_routes

app.register_blueprint(post_routes)
app.register_blueprint(profile_routes)
app.register_blueprint(login_routes)
app.register_blueprint(comment_routes)


if __name__ == "__main__":
    app.run(debug=True)
