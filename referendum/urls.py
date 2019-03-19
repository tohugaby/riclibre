from django.urls import path

from referendum.views import IndexView

urlpatterns = [
    path('', IndexView.as_view(), name='index')
]
