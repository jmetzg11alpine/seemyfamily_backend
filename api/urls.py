from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('', hello_view, name='hello'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('get_profile_data/', get_profile_data, name='get_profile_data'),
    path('get_main_data/', get_main_data, name='get_main_data'),
    path('add_relative/', add_relative, name='add_relative'),
    path('get_all_relatives/', get_all_relatives, name='get_all_relatives'),
    path('update_details/', update_details, name='update_details'),
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('get_photos/', get_photos, name='get_photos'),
    path('custom_login/', custom_login, name='custom_login'),
]
