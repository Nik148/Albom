from flask_mail import Message
from flask import current_app, render_template
from app.tasks import send_email


def send_confirmation_registration(email, token):
    # app = current_app._get_current_object()
    send_email.delay('Albom Confirmation',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[email],
               html_body=render_template('email/email_confirmation_registration.html', token=token))
 
def send_password_reset(user):
    # app = current_app._get_current_object()
    token = user.get_reset_password_token()
    send_email.delay('Albom Reset Your Password',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               html_body=render_template('email/email_reset_password.html',user=user, token=token))