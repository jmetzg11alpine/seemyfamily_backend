from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Photo
from .utils import add_photo


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_photo(request):
    data = request.data
    profile_id = data.get('profileId')
    description = data.get('description', None)
    photo_base64 = data.get('photo_base64')

    profile_pic = Photo.objects.filter(person_id=profile_id).count() <= 0

    add_photo(profile_id, profile_pic, photo_base64, description)

    return Response({'message': f'photo uploaded for id: {profile_id}'})
