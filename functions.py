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


# ---------------------------------- UPDATE USER ------------------------------------
def update_user(user_id, **kwargs):

    user_to_update = User.query.get(user_id)

    for attr, value in kwargs.items():
        setattr(user_to_update, attr, value)

    db.session.add(user_to_update)
    db.session.commit()


# ---------------------------------- UPDATE POST -------------------------------------
def update_post(post_id, tags, **kwargs):

    post_to_update = Post.query.get(post_id)

    if tags:
        tags = [tag.strip() for tag in tags.split(",")]
        for tag in tags:
            existing_tag = Tag.query.filter_by(text=tag).first()
            if existing_tag:
                post_to_update.tags.append(existing_tag)
            else:
                new_tag = Tag(text=tag)
                post_to_update.tags.append(new_tag)

    for attr, value in kwargs.items():
        if value:
            setattr(post_to_update, attr, value)

    db.session.add(post_to_update)
    db.session.commit()


# ---------------------------------- GET POPULAR POSTS ---------------------------------
def get_popular_posts():
    return Post.query.order_by(Post.views.desc()).limit(4).all()


# ----------------------------------- UPLOAD IMG TO S3 ----------------------------------
def upload_to_s3(file, profile_img, acl="public-read"):
    s3 = boto3.client("s3", aws_access_key_id=S3_KEY, aws_secret_access_key=S3_SECRET)

    if file and allowed_file(file.filename):
        print("here we are in upload_to_s3 and there is a file and it is allowed")
        filename = file.filename
        extension = filename.split(".")[-1]
        # create new filename with user id
        new_filename = f"profile-img-user-{current_user.id}.{extension}"
        # save the file to S3 bucket
        print(f"this should be the new_filename = {new_filename}")
        try:
            print(f"the S3 secret is {S3_SECRET}")
            print(f"the S3 access key is {S3_KEY}")
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                new_filename,
                ExtraArgs={"ACL": acl, "ContentType": file.content_type},
            )
            print("uploaded to S3 successfully")
        except Exception as e:
            print(f"Error when uploading to S3: {e}")
            return profile_img
        print(f"this should be returned from the fn = {S3_LOCATION}{new_filename}")
        return f"{S3_LOCATION}{new_filename}"
    else:
        print("something was not right so the profile_img should have stayed the same")
        return profile_img


# ---------------------------------- STR TO KEBAB CASE ----------------------------------
def kebab(str):
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
    my_email = os.environ.get("MAILGUN_SMTP_LOGIN")
    my_email_password = os.environ.get("MAILGUN_SMTP_PASSWORD")
    hash = user.password.split("$")[-1]

    SERVER = os.environ.get("MAILGUN_SMTP_SERVER")
    PORT = os.environ.get("MAILGUN_SMTP_PORT")

    with smtplib.SMTP(SERVER, PORT) as connection:
        connection.ehlo()
        connection.starttls()
        connection.ehlo()
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