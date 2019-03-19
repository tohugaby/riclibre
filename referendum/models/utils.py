"""
Referendum's app :  model's utils
"""
from django.db import models


class FieldUpdateControlMixin(models.Model):
    """
    Mixin that add field update control.
    """
    __control_fields = []

    class Meta:
        abstract = True

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
            if self.pk:
                old_instance = self._meta.model.objects.get(pk=self.pk)
                setattr(self, original_field, getattr(old_instance, field))
