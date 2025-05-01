from django.contrib.auth.models import User

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = {
        'username': details.get('email').split('@')[0],
        'email': details.get('email'),
        'first_name': details.get('first_name', ''),
        'last_name': details.get('last_name', '')
    }

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }