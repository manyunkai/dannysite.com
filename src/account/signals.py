from django.dispatch import Signal

user_signed_up = Signal(providing_args=['user', 'form'])
user_sign_up_attempt = Signal(providing_args=['username', 'email', 'result'])
user_logged_in = Signal(providing_args=['user', 'form'])
user_login_attempt = Signal(providing_args=['username', 'result'])
signup_code_sent = Signal(providing_args=['signup_code'])
signup_code_used = Signal(providing_args=['signup_code_result'])
email_confirmed = Signal(providing_args=['email_address'])
email_confirmation_sent = Signal(providing_args=['confirmation'])
password_changed = Signal(providing_args=['user'])
