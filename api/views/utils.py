from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.exceptions import TokenError
from django.core.files.base import ContentFile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from ..models import Photo, Visitor, History
from django.conf import settings
import base64
from PIL import Image
from io import BytesIO
import time
import os


@api_view(['GET'])
def hello_view(request):
    print('base function "/" was called')
    return Response({'data': 'backend is running'})


@api_view(['POST'])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'messasge': 'Login Successful',
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_name': user.username
            },
            status=status.HTTP_200_OK
        )
    else:
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_login_status(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'message': 'bad'},
            status=status.HTTP_200_OK
        )

    else:
        try:
            token = RefreshToken(refresh_token)
            user = User.objects.get(id=token['user_id'])
            new_access_token = str(token.access_token)

            return Response(
                {
                    'message': 'good',
                    'access': new_access_token,
                    'user_name': user.username
                },
                status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {
                    'message': 'bad'
                },
                status=status.HTTP_200_OK
            )


def get_photo(person):
    photo = Photo.objects.filter(person=person, profile_pic=True).first()
    default_photo_path = 'photos/default.jpeg'

    if not photo:
        return settings.MEDIA_URL + 'photos/default.jpeg', 0

    photo_file_path = os.path.join(settings.MEDIA_ROOT, photo.file_path.name)
    if not os.path.exists(photo_file_path):
        return settings.MEDIA_URL + default_photo_path, 0

    return settings.MEDIA_URL + photo.file_path.name, photo.rotation


def get_inverse_relation(relation):
    if relation == 'Parent':
        return 'Child'
    elif relation == 'Child':
        return 'Parent'
    else:
        return relation


def add_photo(person_id, profile_pic, photo_base64, description):
    if photo_base64.startswith('data:image'):
        photo_base64 = photo_base64.split(',')[1]

    image_data = base64.b64decode(photo_base64)
    image = Image.open(BytesIO(image_data))

    if image.mode == 'RGBA':
        image = image.convert('RGB')

    relative_path = os.path.join(str(person_id), str(time.time()) + '.jpeg')

    max_size = (800, 800)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)

    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_content = ContentFile(image_io.getvalue(), relative_path)

    Photo.objects.create(
        person_id=person_id,
        description=description,
        file_path=image_content,
        profile_pic=profile_pic
    )


def record_ip(request):
    x_forward_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forward_for:
        ip = x_forward_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    today = timezone.now().date()

    Visitor.objects.get_or_create(
        ip_address=ip,
        date=today
    )


def add_to_history(username, recipient, action):
    History.objects.create(
        username=username,
        action=action,
        recipient=recipient
    )
