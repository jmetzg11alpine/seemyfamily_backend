from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from ..models import Person, Photo
from .utils import get_photo, record_ip


@api_view(['GET'])
def get_main_data(request):
    persons = []
    for person in Person.objects.all():
        try:
            location = person.location.name
        except ObjectDoesNotExist:
            location = None

        photo_path, photo_rotation = get_photo(person)

        person_data = {
            'id': person.id,
            'name': person.name,
            'birthdate': person.birthdate,
            'birthplace': person.birthplace,
            'location': location,
            'photo': photo_path,
            'rotation': photo_rotation
        }
        persons.append(person_data)

    user_name = request.user.username if request.user.is_authenticated else None
    record_ip(request)

    return Response({'data': persons, 'userName': user_name})


@api_view(['POST'])
def get_profile_data(request):
    data = request.data
    person_id = data.get('id')

    person = Person.objects.get(id=person_id)
    try:
        location = person.location
    except ObjectDoesNotExist:
        location = None

    photo_path, photo_rotation = get_photo(person)

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
        'photo': photo_path,
        'rotation': photo_rotation
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
