from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import Photo
from .utils import get_photo


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
