from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .token_generator import confirm_email_token_generator


def send_confirmation_code(user):
    template_name = 'account/confirmation_code.html'
    context = {
        'user': user,
        'token': confirm_email_token_generator.make_token(user),
        'uid': urlsafe_base64_encode(force_bytes(user.id))
    }
    template = render_to_string(template_name, context)
    subject = 'Confirm your email'
    mail = EmailMessage(
        subject=subject,
        body=template,
        to=[user.email]
    )
    mail.content_subtype = 'html'
    mail.send()


def send_confirmation_done(user):
    template_name = 'account/confirmation_done.html'
    context = {'user': user}
    template = render_to_string(template_name, context)
    subject = "your account confirmed"
    mail = EmailMessage(
        subject=subject,
        body=template,
        to=[user.email]
    )
    mail.content_subtype = 'html'
    mail.send()