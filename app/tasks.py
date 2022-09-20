from flask_mail import Message
from app import mail, celery



@celery.task
def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    mail.send(msg)
    