from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from ..models import Photo, Person


@api_view(['POST'])
def get_photos(request):
    data = request.data
    profile_id = data.get('profileId')

    all_photos = Photo.objects.filter(person_id=profile_id)
    photos = []

    for photo in all_photos:
        photos.append({
            'id': photo.id,
            'src': settings.MEDIA_URL + photo.file_path.name,
            'description': photo.description,
            'profile_pic': photo.profile_pic,
            'rotation': photo.rotation
        })

    return Response({'photos': photos})
