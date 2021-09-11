import os
import re
import smtplib
from urllib.parse import urljoin, urlparse
from flask import request
from flask_login import current_user
from unidecode import unidecode
from models import Tag, User, Post
from config import (
    ALLOWED_EXTENSIONS,
    db,
    app,
    S3_SECRET,
    S3_KEY,
    S3_SECRET,
    S3_LOCATION,
    S3_BUCKET,
)
import boto3

# ---------------------------------- ALLOWED FILES  ------------------------------------
def allowed_file(filename):
    """returns true if the filename extension is in ALLOWED EXTENSIONS list"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------- SAFE URL ---------------------------------------
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


# ----------------------------- VALIDATE CREDENTIALS ----------------------------------
def validate(email, password, confirm_password):
    """Throws exception if there is an existing user or the passwords don't match. Else returns True"""
    existing_user = User.query.filter_by(email=email).first()
    if bool(existing_user):
        raise UserWarning("Tento email už je zaregistrovaný")
    elif password != confirm_password:
        raise ValueError("Heslá sa musia zhodovať")
    else:
        return True


# -------------------------------- CHECK TAG ORPHANS --------------------------------
def delete_orphan_tag(tag):
    """checks if a tag has no parent and deletes it from database"""
    if len(tag.posts) == 0:
        db.session.delete(tag)
        db.session.commit()
        return True
    else:
        return False


# ---------------------------------- UPDATE USER ------------------------------------
def update_user(user_id, **kwargs):

    user_to_update = User.query.get(user_id)

    for attr, value in kwargs.items():
        setattr(user_to_update, attr, value)

    db.session.commit()


# ---------------------------------- UPDATE POST -------------------------------------
def update_post(post_id, tags, **kwargs):
    post_to_update = Post.query.get(post_id)
    old_tags = [tag.name for tag in post_to_update.tags]

    if tags:
        new_tags = [tag.strip() for tag in tags.split(",")]

        for tag in post_to_update.tags:
            if not tag.name in new_tags:
                post_to_update.tags.remove(tag)
                delete_orphan_tag(tag)

        for tag in new_tags:
            existing_tag = Tag.query.filter_by(name=tag).first()
            if existing_tag and tag in old_tags:
                pass
            elif existing_tag:
                post_to_update.tags.extend([existing_tag])
            else:
                new_tag = Tag(name=tag)
                post_to_update.tags.extend([new_tag])

    elif old_tags and not tags:
        for tag in post_to_update.tags:
            post_to_update.tags.remove(tag)
            delete_orphan_tag(tag)

    for attr, value in kwargs.items():
        if value:
            setattr(post_to_update, attr, value)

    db.session.commit()


# ---------------------------------- GET POPULAR POSTS ---------------------------------
def get_popular_posts():
    """returns four posts with the most views"""
    return Post.query.order_by(Post.views.desc()).limit(4).all()


# ----------------------------------- UPLOAD IMG TO S3 ----------------------------------
def upload_to_s3(file, profile_img, acl="public-read"):
    """uploads the file to the AWS S3 bucket"""
    s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

    if file and allowed_file(file.filename):
        filename = file.filename
        extension = filename.split(".")[-1]
        # create new filename with user id
        new_filename = f"profile-img-user-{current_user.id}.{extension}"
        # save the file to S3 bucket
        try:
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                new_filename,
                ExtraArgs={"ACL": acl, "ContentType": file.content_type},
            )
        except Exception as e:
            print(f"Error when uploading to S3: {e}")
            return profile_img
        return f"{S3_LOCATION}{new_filename}"
    else:
        return profile_img


# ---------------------------------- STR TO KEBAB CASE ----------------------------------
def kebab(str):
    """changes string to kebab case"""
    str = re.sub("[^a-zA-Z0-9\s:-]", "", str)
    str = unidecode(str).lower()
    x = re.findall(
        "(?:\d+)|(?:[a-zA-Z]+(?=\d))|(?:[a-zA-Z0-9]+(?=[A-Z]))|(?:[a-zA-Z0-9]+(?=\-))|(?:[a-zA-Z0-9]+(?=\s))|[a-zA-Z0-9]+$",
        str,
    )
    x = "-".join(x)
    return x


# makes the function accessible in the templates
app.jinja_env.globals.update(kebab=kebab)


# ---------------------------------------- SEND EMAIL -------------------------------------------
def send_password_reset_link(user):
    my_email = os.environ.get("SMTP_LOGIN")
    my_email_password = os.environ.get("SMTP_PASSWORD")
    hash = user.password.split("$")[-1]

    SERVER = os.environ.get("SMTP_SERVER")
    PORT = os.environ.get("SMTP_PORT")

    with smtplib.SMTP(SERVER, PORT) as connection:
        connection.ehlo()
        connection.starttls()
        connection.login(user=my_email, password=my_email_password)
        try:
            connection.sendmail(
                from_addr=my_email,
                to_addrs=user.email,
                msg=f"Subject:HVIZD Resetovanie hesla!\n\nPre zresetovanie hesla na hvizd.sk kliknite na tento link\nhttps://hvizd-blog.sk/password-reset/{user.id}/{hash}",
            )
        except Exception as e:
            print(e)
            return


# --------------------------------------- PRETTY DATE -------------------------------------------


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime

    now = datetime.now()

    diff = now - time

    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""

    if day_diff == 0:
        if second_diff < 10:
            return "práve teraz"
        if second_diff < 60:
            return f"pred {second_diff} sekundami"
        if second_diff < 120:
            return "pred minútou"
        if second_diff < 3600:
            return f"pred {second_diff // 60} minútami"
        if second_diff < 7200:
            return "pred hodinou"
        if second_diff < 86400:
            return f"pred {second_diff // 3600} hodinami"
    if day_diff == 1:
        return "Včera"
    if day_diff < 7:
        return f"pred {day_diff} dňami"
    if day_diff < 31:
        if day_diff // 7 > 1:
            return f"pred {day_diff // 7} týždňami"
        else:
            return f"pred týždňom"
    if day_diff < 365:
        if day_diff // 30 > 1:
            return f"pred {day_diff // 30} mesiacmi"
        else:
            return "pred mesiacom"
    if day_diff // 365 == 1:
        return "pred rokom"
    return f"pred {day_diff // 365} rokmi"


# makes the function accessible in the templates
app.jinja_env.globals.update(pretty_date=pretty_date)