"""
Custom validators
"""
import string

from django.core.exceptions import ValidationError
from django.utils.translation import gettext


class RequiredCharactersValidator:
    """
    A password validator that check if password contains requiredCharacters.
    """

    def __init__(self):
        self.required_chars_group_list = [string.ascii_lowercase, string.ascii_uppercase, string.digits,
                                          string.punctuation]

        # escaped_required_chars = []
        # for char_list in self.required_chars_group_list:
        #     escaped_required_chars.append(list(map(escape, char_list)))
        #
        #
        # self.message = """
        # Le mot de passe doit contenir au moins une lettre minuscule ({}), une lettre majuscule ({}), un chiffre (
        # {}) et un caractère spécial ({}).
        # """.format(*escaped_required_chars)
        self.message = """
        Le mot de passe doit contenir au moins une lettre minuscule, une lettre majuscule, un chiffre et un caractère
        spécial.
        """

    def validate(self, password, user=None):
        """
        Checks if password contains required characters.
        :param password: a user password
        :param user: a user instance unused in this method
        :return: Nothing or raise an error
        """
        missing_char = False
        for chars_group in self.required_chars_group_list:
            if not any(char in password for char in chars_group):
                missing_char = True
                break

        if missing_char:
            raise ValidationError(gettext(self.message),
                                  code='required_char_missing',
                                  params={'required_chars_group_list': self.required_chars_group_list},
                                  )

    def get_help_text(self):
        """
        Just return help message associated to validator.
        :return:
        """
        return self.message
