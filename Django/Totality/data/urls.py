from django.urls import path
from .views import *

urlpatterns = [
    path('data', data, name='data-push'),
    # path('registration', registration, name='data-registration'),
]
