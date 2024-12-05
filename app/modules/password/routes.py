from flask import flash, redirect, render_template, request, url_for
from app.modules.password import password_bp
from app.modules.password.services import PasswordService
from itsdangerous import BadTimeSignature, SignatureExpired

password_service = PasswordService()


@password_bp.route('/password', methods=['GET'])
def index():
    return render_template('password/index.html')


@password_bp.route('/forgot/password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            if not email:
                flash('Please enter a valid email address', 'danger')
                return redirect(url_for('password.forgot_password'))

            password_service.send_change_password_email(email)
            flash('Check your email for the instructions to change your password', 'success')
            return redirect(url_for('auth.login'))

        except Exception as exc:
            flash(f'An error occurred while trying to change the password: {exc}', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('password/forgot_password.html')


@password_bp.route('/change/password/<token>', methods=['GET', 'POST'])
def change_password(token):
    try:
        email = password_service.get_email_by_token(token)
    except SignatureExpired:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.login'))
    except BadTimeSignature:
        flash('The reset link has expired.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form['password']
        password_service.change_password(email=email, password=password)
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('password/change_password.html')
