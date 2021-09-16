from flask import request, redirect, url_for, render_template, Blueprint, flash, abort
from flask_login.utils import login_user, logout_user, login_required
from config import db
from models import User
from functions import validate, is_safe_url, send_password_reset_link, update_user
from werkzeug.security import check_password_hash, generate_password_hash

login_routes = Blueprint("login_routes", __name__)


@login_routes.route("/login", methods=["GET", "POST"])
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
            return redirect(url_for("login_routes.login"))

    return render_template("login.html", title="Hvizd - Prihlásenie")


@login_routes.route("/register", methods=["GET", "POST"])
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
            return redirect(url_for("login_routes.register"))
        except ValueError as error:
            flash(str(error))
            return redirect(url_for("login_routes.register"))
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

    return render_template("register.html", title="Hvizd - Registrácia")


@login_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@login_routes.route("/password-reset-request", methods=["GET", "POST"])
def password_reset_request():
    if request.method == "POST":
        email = request.form["email"]
        print(f"email je {email}")
        user = User.query.filter_by(email=email).first()
        send_password_reset_link(user)
        return redirect(url_for("login_routes.login"))

    return render_template("password-reset.html", request=True)


@login_routes.route(
    "/password-reset/<int:user_id>/<string:hash>", methods=["GET", "POST"]
)
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
            return redirect(
                url_for("login_routes.password_reset", user_id=user_id, hash=hash)
            )
    return render_template(
        "password-reset.html",
        user_id=user_id,
        hash=hash,
        request=False,
        title="Hvizd - Obnova hesla",
    )
