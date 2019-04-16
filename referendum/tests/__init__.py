"""
Referendum's app: tests module
"""
from django.contrib.auth import get_user_model


def create_test_user(password, is_active=True):
    """
    Return a unique test user
    :return:
    """
    user = get_user_model().objects.create(username='test', email='test@test.fr', is_active=is_active)
    user.set_password(password)
    user.save()
    return user

REFERENDUM_DATA = {
    "title": "referendum de test",
    "description": "ceci est un referendum de test",
    "question": "êtes-vous d'accord ?",
    "creator_id": 1
}
