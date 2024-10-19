from django.urls import path
from .views import *

from .views_temp.utils import hello_view
from .views_temp.view_profiles import (
    get_main_data, get_profile_data, get_all_relatives
)
from .views_temp.edit_profiles import (UpdateDetails, AddRelative)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    # utils
    path('', hello_view, name='hello'),

    # view_profiles
    path('get_main_data/', get_main_data, name='get_main_data'),
    path('get_profile_data/', get_profile_data, name='get_profile_data'),
    path('get_all_relatives/', get_all_relatives, name='get_all_relatives'),

    # edit_profiles
    path('add_relative/', AddRelative.as_view(), name='add_relative'),
    path('update_details/', UpdateDetails.as_view(), name='update_details'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('get_photos/', get_photos, name='get_photos'),
    path('custom_login/', custom_login, name='custom_login'),
]
