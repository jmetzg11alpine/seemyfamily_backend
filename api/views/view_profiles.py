from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ..models import Person, Photo
from .utils import get_photo


@api_view(['GET'])
def get_main_data(request):
    persons = Person.objects.select_related('location').values('id', 'name', 'birthdate', 'birthplace', 'location__name')
    user_name = None
    if request.user.is_authenticated:
        user_name = request.user.user_name

    return Response({'data': persons, 'userName': user_name})


@api_view(['POST'])
def get_profile_data(request):
    data = request.data
    person_id = data.get('id')

    person = Person.objects.get(id=person_id)
    location = person.location.first()
    photo = Photo.objects.filter(person=person, profile_pic=True).first()

    profile_data = {
        'id': person.id,
        'name': person.name,
        'birthdate': person.birthdate,
        'birthplace': person.birthplace,
        'bio': person.bio,
        'relations': person.relations,
        'location': location.name if location else None,
        'lat': location.lat if location else None,
        'lng': location.lng if location else None,
        'photo': get_photo(photo)
    }

    return Response({'profile_data': profile_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_all_relatives(request):
    data = request.data

    profile_relations = Person.objects.filter(id=data.get('id')).values('id', 'relations').first()
    relation_ids = {relation['id'] for relation in profile_relations['relations']}
    relation_ids.add(profile_relations['id'])

    possible_relatives = Person.objects.exclude(id__in=relation_ids).values('id', 'name')
    relative_options = [
        {'id': person['id'], 'value': person['name'], 'label': person['name']}
        for person in possible_relatives
    ]

    return Response({'relative_options': relative_options}, status=status.HTTP_200_OK)
