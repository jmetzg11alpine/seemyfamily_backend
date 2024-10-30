from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import History


@api_view(['POST'])
def get_edits(request):
    data = History.objects.all().order_by('-created_at')

    history_data = [
        {
            'id': item.id,
            'created_at': item.created_at,
            'username': item.username,
            'action': item.action,
            'recipient': item.recipient
        } for item in data
    ]
    return Response({'data': history_data})
