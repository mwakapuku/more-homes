from django.contrib.auth.hashers import make_password


def change_user_password(user, password):
    user.reset_otp = False
    user.password = make_password(password)
    user.save()
