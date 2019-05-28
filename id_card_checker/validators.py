"""
Id_card_checker's app:  IdCard's validators module
"""
import logging

from django.conf import settings
from django.core.exceptions import ValidationError

LOGGER = logging.getLogger(__name__)

SIZE_LIMITATION_TEXT = "Vous ne pouvez pas soumettre un fichier d'une taille supérieure à %s."


def get_human_readable_file_size(byte_size):
    """
    Return a string after converting byte size to human readable size.
    :param byte_size: size in byte.
    :return: human readable size
    """
    base_size = 1024.00
    measures = ["B", "KB", "MB", "GB", "TB", "PB"]

    readable_size = float(byte_size)
    measure_index = 0

    while readable_size > base_size:
        readable_size = readable_size / base_size
        measure_index += 1

    return "{:.0f} {}".format(readable_size, measures[measure_index])


def validate_file_size(value):
    """
    Validate file size according to settings
    :param value: element to validate.
    """
    if hasattr(settings, 'MAX_ID_CARD_FILE_SIZE'):
        max_size_in_mb = get_human_readable_file_size(settings.MAX_ID_CARD_FILE_SIZE)
        if value.size > settings.MAX_ID_CARD_FILE_SIZE:
            message = SIZE_LIMITATION_TEXT % max_size_in_mb
            LOGGER.warning(message)
            raise ValidationError(message)
