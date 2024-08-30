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
    data = request.data

    profile_person = Person.objects.get(id=data.get('profileId'))

    new_relative = create_new_relative(data)

    profile_person.relations.append({
        'id': new_relative.id,
        'name': new_relative.name,
        'relation': data['relation']
    })
    profile_person.save()

    add_relations(data, new_relative, profile_person)

    return Response({'message': 'Relative added successfully'}, status=status.HTTP_200_OK)
