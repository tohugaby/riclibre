"""
Referendum's app: views utilities
"""
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class UserIsAnonymousMixin(UserPassesTestMixin):
    """
    Mixin to control that user is not logged in.
    """

    def test_func(self):
        """
        Test if user is anonymous.
        :return:
        """
        return self.request.user.is_anonymous

    def dispatch(self, request, *args, **kwargs):
        """
        Override dispatch method. Apply test_func
        """
        user_test_result = self.get_test_func()()
        if not user_test_result:
            return HttpResponseRedirect(reverse_lazy('index'))
        return super().dispatch(request, *args, **kwargs)
