from flask_login import UserMixin
from config import DEFAULT_POST_IMG, db
import datetime


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