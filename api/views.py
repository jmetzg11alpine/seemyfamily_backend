from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .models import Person, Location, Photos
from .helpers import create_new_relative, add_relations

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def hello_view(request):
    print('i was called')
    return Response({'data': 'hello'})


@api_view(['GET'])
def get_main_data(request):
    persons = Person.objects.values('id', 'name', 'birthdate', 'birthplace')
    return Response({'data': persons})


@api_view(['POST'])
def get_profile_data(request):
    data = request.data
    person_id = data.get('id')

    person = Person.objects.get(id=person_id)
    location = person.location.first()

    profile_data = {
        'id': person.id,
        'name': person.name,
        'birthdate': person.birthdate,
        'birthplace': person.birthplace,
        'bio': person.bio,
        'relations': person.relations,
        'location': location.name if location else None
    }

    return Response({'profile_data': profile_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_relative(request):
    data = request.data['newProfile']
    print(data)

    profile_person = Person.objects.get(id=data.get('profileId'))

    new_relative = create_new_relative(data)

    add_relations(data, new_relative, profile_person)

    profile_person.relations.append({
        'id': new_relative.id,
        'name': new_relative.name,
        'relation': data['relation']
    })
    profile_person.save()

    return Response({'message': 'Relative added successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_all_relatives(request):
    data = request.data

    profile_relations = Person.objects.filter(id=data.get('id')).values('relations').first()
    relation_ids = {relation['id'] for relation in profile_relations['relations']}

    possible_relatives = Person.objects.exclude(id__in=relation_ids).values('id', 'name')
    relative_options = [
        {'id': person['id'], 'value': person['name'], 'label': person['name']}
        for person in possible_relatives
    ]

    return Response({'relative_options': relative_options}, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_details(request):
    data = request.data
    print(data)

    return Response({'message': f'{data.name} was updated'})
