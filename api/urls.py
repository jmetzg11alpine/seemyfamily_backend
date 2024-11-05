from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from .views.utils import hello_view, custom_login, check_login_status
from .views.view_profiles import (
    get_main_data, get_profile_data, get_all_relatives
)
from .views.edit_profiles import UpdateDetails, AddRelative, DeleteProfile
from .views.view_photos import get_photos
from .views.edit_photos import upload_photo, edit_photo, delete_photo
from .views.view_info import get_edits, get_visitors, get_geo_data

urlpatterns = [
    # utils
    path('', hello_view, name='hello'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('custom_login/', custom_login, name='custom_login'),
    path('check_login_status/', check_login_status, name='check_login_status'),

    # view_profiles
    path('get_main_data/', get_main_data, name='get_main_data'),
    path('get_profile_data/', get_profile_data, name='get_profile_data'),
    path('get_all_relatives/', get_all_relatives, name='get_all_relatives'),

    # edit_profiles
    path('add_relative/', AddRelative.as_view(), name='add_relative'),
    path('update_details/', UpdateDetails.as_view(), name='update_details'),
    path('delete_profile/', DeleteProfile.as_view(), name='delete_profile'),

    # view photos
    path('get_photos/', get_photos, name='get_photos'),

    # edit photos
    path('upload_photo/', upload_photo, name='upload_photo'),
    path('edit_photo/', edit_photo, name='edit_photo'),
    path('delete_photo/', delete_photo, name='delete_photo'),

    # info
    path('get_edits', get_edits, name='get_edits'),
    path('get_visitors/', get_visitors, name='get_visitors'),
    path('get_geo_data', get_geo_data, name='get_geo_data')
]
