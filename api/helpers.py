from django.core.files.base import ContentFile
from django.conf import settings
from .models import Person, Location, Photo
from collections import defaultdict
import base64
import time
from PIL import Image
from io import BytesIO
import os


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
        if relative_relation == 'Sibling' and profile_relation in ['Parent', 'Sibling']:
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name},
                    'Parent' if profile_relation == 'Parent' else 'Sibling'
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
