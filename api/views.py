from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from .models import Person, Location, Photos


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def hello_view(request):
    return Response({'data': 'hello'})
