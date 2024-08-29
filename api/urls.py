from django.urls import path
from .views import *

urlpatterns = [
    path('', hello_view, name='hello'),
    path('get_profile_data', get_profile_data, name='get_profile_data'),
    path('get_main_data', get_main_data, name='get_main_data'),
    path('add_relative', add_relative, name='add_relative')
]
