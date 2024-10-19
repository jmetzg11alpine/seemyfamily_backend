from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.core.files.base import ContentFile
from ..models import Photo
import base64
from PIL import Image
from io import BytesIO
import time
import os


@api_view(['GET'])
def hello_view(request):
    print('base function "/" was called')
    return Response({'data': 'backend is running'})


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
