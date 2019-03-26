"""
Referendum's app: form's utils
"""


def help_text_list_to_span(help_text):
    """
    Transform help text list to html list of span
    :param help_text: a list or one help text
    :return: html string
    """
    if not isinstance(help_text, str):
        help_text = list(help_text)
    return '<br>'.join(['<span>%s</span>' % text for text in help_text])
