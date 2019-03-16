"""
Referendum's app :  model's utils
"""


class FieldUpdateControlMixin:
    """
    Mixin that add field update control.
    """
    __control_fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_control_fields(*self.__control_fields)

    def update_control_fields(self, *control_fields):
        """
        Update control field to monitor changes
        :return:
        """
        fields = control_fields if control_fields else self.__control_fields
        for field in fields:
            original_field = "__original_%s" % field
            setattr(self, original_field, getattr(self, field))
