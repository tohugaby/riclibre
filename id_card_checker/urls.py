from django.urls import path

from id_card_checker.views import IdCardUploadView

urlpatterns = [
    path('idcard', IdCardUploadView.as_view(), name='idcard')
]
