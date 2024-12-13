from flask import flash, render_template, redirect, url_for, request
from flask_login import current_user, logout_user
from pymysql import IntegrityError

from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService
from app.modules.signupvalidation.services import SignupvalidationService
from app import db


authentication_service = AuthenticationService()
user_profile_service = UserProfileService()
signupvalidation_service = SignupvalidationService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template(
                "auth/signup_form.html", form=form, error=f"Email {email} in use"
            )

        try:
            # We try to create the user
            user = authentication_service.create_with_profile(**form.data)
            signupvalidation_service.send_confirmation_email(user.email)

        except IntegrityError as exc:
            db.session.rollback()
            if "Duplicate entry" in str(exc):
                flash(f"Email {email} is already in use", "danger")
            else:
                flash(f"Error creating user: {exc}", "danger")
            return render_template("auth/signup_form.html", form=form)

        return redirect(
            url_for("signupvalidation.index")
        )  # enviar a esperar verificación

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.index"))

    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        if authentication_service.login(form.email.data, form.password.data):
            return redirect(url_for("public.index"))

        return render_template(
            "auth/login_form.html", form=form, error="Invalid credentials"
        )

    return render_template("auth/login_form.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("public.index"))
