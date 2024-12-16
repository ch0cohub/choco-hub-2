from flask import flash, redirect, render_template, url_for
from app.modules.signupvalidation import signupvalidation_bp
from app.modules.signupvalidation.services import SignupvalidationService


signupvalidation_service = SignupvalidationService()


@signupvalidation_bp.route("/signupvalidation", methods=["GET"])
def index():
    return render_template("signupvalidation/index.html")


@signupvalidation_bp.route("/confirm_user/<token>", methods=["GET"])
def confirm_user(token):
    try:
        signupvalidation_service.confirm_user_with_token(token)
    except Exception as exc:
        flash(exc.args[0], "danger")
        return redirect(url_for("auth.show_signup_form"))

    return redirect(url_for("public.index"))
