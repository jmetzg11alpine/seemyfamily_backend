from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from ..models import Photo, Person
from .utils import add_photo, add_to_history
import os

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_photo(request):
    data = request.data
    profile_id = data.get('profileId')
    description = data.get('description', None)
    photo_base64 = data.get('photo_base64')

    profile_pic = Photo.objects.filter(person_id=profile_id).count() <= 0

    add_photo(profile_id, profile_pic, photo_base64, description)

    person = Person.objects.get(id=profile_id)
    add_to_history(request.user.username, person.name, 'added photo')

    return Response({'message': 'photo uploaded', 'profile': profile_pic})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_photo(request):
    data = request.data
    photo_id = data.get('id')
    profile_pic_changed = data.get('profilePicChanged')
    profile_pic = data.get('profile_pic')
    description = data.get('description')

    photo_instance = Photo.objects.get(id=photo_id)

    person_name = photo_instance.person.name

    if profile_pic_changed and photo_instance.profile_pic:
        photo_instance.profile_pic = False

        if not profile_pic:
            other_random_photo = Photo.objects.filter(
                profile_pic=False,
                person=photo_instance.person
            ).first()
            if not other_random_photo:
                photo_instance.profile_pic = True
            else:
                other_random_photo.profile_pic = True
                other_random_photo.save()
    else:
        photo_instance.profile_pic = profile_pic
        photo_instance.description = description

    photo_instance.save()
    add_to_history(request.user.username, person_name, 'edited photot')

    return Response({'message': 'photo edited'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_photo(request):
    data = request.data
    photo_id = data.get('id')

    photo_instance = Photo.objects.get(id=photo_id)
    person_name = photo_instance.person.name

    if photo_instance.profile_pic:
        other_random_photo = Photo.objects.filter(
            profile_pic=False,
            person=photo_instance.person
        ).first()
        if other_random_photo:
            other_random_photo.profile_pic = True
            other_random_photo.save()

    photo_path = os.path.join(settings.MEDIA_ROOT, str(photo_instance.file_path))
    if os.path.exists(photo_path):
        os.remove(photo_path)

    photo_instance.delete()
    add_to_history(request.user.username, person_name, 'deleted photo')

    return Response({'message': 'photo deleted'}, status=status.HTTP_200_OK)
