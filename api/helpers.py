from collections import defaultdict
from .models import Person, Location, Photo
import base64
import time
from PIL import Image
from io import BytesIO
import os


def create_new_relative(data):
    birthday = data.get('birthdate')
    birthplace = data.get('birthplace') or ''
    bio = data.get('bio') or ''
    if birthday == 'undefined' or birthday == '':
        birthday = None

    person = Person.objects.create(
        name=data.get('name'),
        birthdate=birthday,
        birthplace=birthplace,
        bio=bio,
    )

    add_location(data, person)

    return person


def add_location(data, person):
    location_name = data.get('location')
    lat, lng = data.get('lat'), data.get('lng')
    if location_name:
        try:
            lat, lng = float(lat), float(lng)
        except (TypeError, ValueError):
            lat, lng = None, None,

        location, created = Location.objects.get_or_create(
            person=person,
            defaults={
                'name': location_name,
                'lat': lat,
                'lng': lng
            }
        )

        if not created:
            location.name = location_name
            location.lat = lat
            location.lng = lng
            location.save()


def get_inverse_relation(relation):
    if relation == 'Parent':
        return 'Child'
    elif relation == 'Child':
        return 'Parent'
    else:
        return relation


def add_relations(data, new_relative, profile_person):

    def create_relation_entry(person_dict, relation):
        return {
            'id': person_dict['id'],
            'name': person_dict['name'],
            'relation': relation
        }

    profile_relation = data['relation']
    new_relation = get_inverse_relation(profile_relation)
    new_relations = [create_relation_entry({'id': profile_person.id, 'name': profile_person.name}, new_relation)]

    relations_to_add = defaultdict(list)

    for relative in profile_person.relations:
        relative_relation = relative['relation']

        # relations for new relative
        if relative_relation == 'Parent' and profile_relation == 'Sibling':
            new_relations.append(relative)
        if relative_relation == 'Parent' and profile_relation == 'Parent':
            new_relations.append(create_relation_entry(relative, 'Spouse'))
        elif relative_relation == 'Sibling' and profile_relation in ['Parent', 'Sibling']:
            new_relations.append(
                create_relation_entry(
                    relative, 'Child' if profile_relation == 'Parent' else 'Sibling'
                )
            )
        elif relative_relation == 'Child' and profile_relation in ['Child', 'Spouse']:
            new_relations.append(
                create_relation_entry(
                    relative, 'Child' if profile_relation == 'Spouse' else 'Sibling'
                )
            )
        elif relative_relation == 'Spouse' and profile_relation == 'Child':
            new_relations.append(create_relation_entry(relative, 'Parent'))

        # prepare for reverse additon of relatives
        if relative_relation == 'Sibling' and profile_relation == 'Parent':
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name}, 'Parent'
                )
            )
        elif relative_relation == 'Parent' and profile_relation in ['Sibling', 'Parent']:
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name},
                    'Child' if profile_relation == 'Sibling' else 'Spouse'
                )
            )
        elif relative_relation == 'Child' and profile_relation in ['Child', 'Spouse']:
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name},
                    'Sibling' if profile_relation == 'Child' else 'Parent'
                )
            )
        elif relative_relation == 'Spouse' and profile_relation == 'Child':
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name}, 'Child'
                )
            )

    new_relative.relations = new_relations
    new_relative.save()

    reverse_add_relatives(relations_to_add)


def reverse_add_relatives(relations):
    for id in relations:
        person = Person.objects.get(id=id)
        for entry in relations[id]:
            person.relations.append(entry)
        person.save()


def add_one_relative(edit_person, profile_data):
    new_relative_id = profile_data['person_add']['id']
    new_relative_relation = profile_data['relation_add']['value']

    new_relative_instance = Person.objects.filter(id=new_relative_id).first()

    new_relative = {
        'id': new_relative_id,
        'name': new_relative_instance.name,
        'relation': new_relative_relation
    }
    edit_person.relations.append(new_relative)

    new_relation = get_inverse_relation(new_relative_relation)

    new_relative_instance.relations.append({
        'id': edit_person.id,
        'name': edit_person.name,
        'relation': new_relation
    })
    new_relative_instance.save()


def remove_one_relative(person, id_to_remove):
    def remove_person(person, id_to_remove):
        relations_to_keep = []
        for relation in person.relations:
            if relation['id'] != id_to_remove:
                relations_to_keep.append(relation)
        person.relations = relations_to_keep

    remove_person(person, id_to_remove)

    other_relative = Person.objects.filter(id=id_to_remove).first()
    remove_person(other_relative, person.id)
    other_relative.save()


def get_photo(photo):
    if not photo:
        file_path = 'api/data/photos/default.jpeg'
    else:
        file_path = os.path.join('api/data/photos', photo.file_path)
    with open(file_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def add_photo(person, profile_pic, photo_base64):
    if photo_base64.startswith('data:image'):
        photo_base64 = photo_base64.split(',')[1]
    image_data = base64.b64decode(photo_base64)
    image = Image.open(BytesIO(image_data))
    max_size = (800, 800)
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    file_path = f'{person.id}/{int(time.time())}.jpeg'

    full_path = os.path.join('api/data/photos', file_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    image.save(full_path, format='JPEG')

    Photo.objects.create(
        person=person,
        file_path=file_path,
        profile_pic=profile_pic
    )
