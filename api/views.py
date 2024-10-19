from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .models import Person, Photo
from .helpers import add_photo
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


@api_view(['POST'])
def upload_photo(request):
    data = request.data
    profile_id = data.get('profileId')
    description = data.get('description', None)
    photo_base64 = data.get('photo_base64')

    profile_pic = Photo.objects.filter(person_id=profile_id).count() <= 0

    add_photo(profile_id, profile_pic, photo_base64, description)

    return Response({'message': f'photo uploaded for id: {profile_id}'})


@api_view(['POST'])
def get_photos(request):
    data = request.data
    profile_id = data.get('profileId')

    all_photos = Photo.objects.filter(person_id=profile_id)
    photos = []
    for photo in all_photos:
        photos.append({
            'src': get_photo(photo),
            'description': photo.description,
            'profile_pic': photo.profile_pic
        })

    return Response({'photos': photos})

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
# from django.views.decorators.csrf import csrf_exempt

# from django.middleware.csrf import get_token


@api_view(['POST'])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'messasge': 'Login Successful',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
