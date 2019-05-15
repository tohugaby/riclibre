from django.utils import timezone


def transform_year(two_digit_year: str):
    """
    get 4 digit year from 2 digit year
    :param two_digit_year: a two digits year string
    :return: a 4 digit year string
    """
    if timezone.now().strftime('%y') > str(two_digit_year):
        return f'20{two_digit_year}'
    return f'19{two_digit_year}'


def transform_birth_date(birth_date: str):
    """
    Provide 8 digit formated birth date from 6 digit reversed birth date
    :param birth_date: 6 digits reverse birth date
    :return: 8 digits formated birth date
    """
    year = int(transform_year(birth_date[:2]))
    month = int(birth_date[2:4])
    day = int(birth_date[4:])
    return timezone.datetime(year, month, day).strftime('%d/%m/%Y')


def clean_stuffing_char(extracted_string: str):
    """
    Replace stuffing char with space
    :param extracted_string: a string to clean
    :return: cleaned string
    """
    return extracted_string.replace('<', ' ')


french_structure = {
    'type': {'interval': (0, 2), 'methods': []},
    'country': {'interval': (2, 5), 'methods': []},
    'last_name': {'interval': (5, 30), 'methods': [clean_stuffing_char, str.strip]},
    'admin_code': {'interval': (30, 36), 'methods': []},
    'delivery_year': {'interval': (36, 38), 'methods': [transform_year]},
    'delivery_month': {'interval': (38, 40), 'methods': []},
    'department': {'interval': (40, 42), 'methods': []},
    'number': {'interval': (42, 48), 'methods': []},
    'first_control_key': {'interval': (48, 49), 'methods': []},
    'first_names': {'interval': (49, 63), 'methods': [clean_stuffing_char, str.strip]},
    'birth_date': {'interval': (63, 69), 'methods': [transform_birth_date]},
    'second_control_key': {'interval': (69, 70), 'methods': []},
    'gender': {'interval': (70, 71), 'methods': []},
    'third_control_key': {'interval': (71,), 'methods': []}
}


def french_mrz_control_key(string):
    """
    Check a part of mrz.
    :param string:
    :return:
    """
    code = string
    result = 0
    i = -1
    factor = [7, 3, 1]

    for car in code:
        if car == "<":
            value = 0
            i += 1
        elif car in "0123456789":
            value = int(car)
            i += 1
        elif car in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            value = ord(car) - 55
            i += 1
        else:
            print("Caractère hors bornes")
            break

        result += value * factor[i % 3]
    return result % 10


def check_french_mrz(mrz_text):
    """
    Check full french ID mrz
    :param mrz_text:
    :return:
    """
    return french_mrz_control_key(mrz_text[36:48]) == int(mrz_text[48]) and french_mrz_control_key(
        mrz_text[63:69]) == int(mrz_text[69]) and french_mrz_control_key(mrz_text[:-1]) == int(mrz_text[-1])


def apply_structure(struct: dict, mrz_text: str):
    """
    Apply structure and methods to provided mrz_text
    :param struct:
    :param mrz_text:
    :return:
    """
    start = struct['interval'][0]
    end = struct['interval'][1] if len(struct['interval']) > 1 else None
    extracted_value = mrz_text[start:end] if end else mrz_text[start]
    for funct in struct['methods']:
        extracted_value = funct(extracted_value)
    return extracted_value


def split_mrz(structure_dict: dict, mrz_text: str) -> dict:
    """
    Parse mrz_text by using provided structure.
    :param structure_dict: a dict describing structure
    :param mrz_text: a string representing mrz
    :return: a parsed mrz
    """
    return {key: apply_structure(value, mrz_text) for key, value in structure_dict.items()}
