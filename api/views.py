from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from .models import Person, Photo
from .helpers import create_new_relative, add_location, add_relations, add_one_relative, remove_one_relative, get_photo, add_photo


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def hello_view(request):
    print('base function "/" was called')
    return Response({'data': 'backend is running'})


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_main_data(request):
    persons = Person.objects.select_related('location').values('id', 'name', 'birthdate', 'birthplace', 'location__name')
    return Response({'data': persons})


@api_view(['POST'])
@renderer_classes([JSONRenderer])
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
@renderer_classes([JSONRenderer])
def add_relative(request):
    data = request.data['newProfile']

    profile_person = Person.objects.get(id=data.get('profileId'))

    new_relative = create_new_relative(data)

    add_relations(data, new_relative, profile_person)

    if 'photo_base64' in data:
        add_photo(new_relative.id, True, data['photo_base64'], None)

    profile_person.relations.append({
        'id': new_relative.id,
        'name': new_relative.name,
        'relation': data['relation']
    })
    profile_person.save()

    return Response({'message': 'Relative added successfully'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
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


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def update_details(request):
    data = request.data
    profile_data = data.get('profileData')
    person = Person.objects.filter(id=profile_data.get('id')).first()

    for key in ['name', 'birthdate', 'birthplace', 'bio']:
        setattr(person, key, profile_data.get(key))

    add_location(profile_data, person)

    if 'person_add' in profile_data:
        add_one_relative(person, profile_data)

    if 'relation_remove' in profile_data:
        remove_one_relative(person, profile_data['relation_remove'])

    person.save()

    return Response({'message': f'{profile_data['name']} was updated'})


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def upload_photo(request):
    data = request.data
    profile_id = data.get('profileId')
    description = data.get('description', None)
    photo_base64 = data.get('photo_base64')

    profile_pic = Photo.objects.filter(person_id=profile_id).count() <= 0

    add_photo(profile_id, profile_pic, photo_base64, description)

    return Response({'message': f'photo uploaded for id: {profile_id}'})


@api_view(['POST'])
@renderer_classes([JSONRenderer])
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
