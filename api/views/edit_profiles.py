from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from ..models import Person, Location
from .utils import get_inverse_relation, add_photo
from collections import defaultdict
import os


class AddRelative(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data['newProfile']

        profile_person = Person.objects.get(id=data.get('profileId'))
        new_person = self.create_new_relative(data)

        self.add_relations(data, new_person, profile_person)
        self.add_new_relative_photo(data, new_person)
        self.update_profile_person(profile_person, new_person, data)

        # Good for debugging:
        print(f"PROFILE RELATION: {data['relation']}, PROFILE NAME: {profile_person.name}")
        print('PROFILE PERSON RELATIONS:')
        print(profile_person.relations)
        print(f'PERSON ADDED: {new_person.name}')

        return Response(
            {'message': 'Relative added successfully'},
            status=status.HTTP_200_OK
        )

    def create_new_relative(self, data):
        person = Person.objects.create(
            name=data.get('name'),
            birthdate=data.get('birthdate', None),
            birthplace=data.get('birthplace', None),
            bio=data.get('bio', None)
        )
        self.add_location(data, person)
        return person

    def add_location(self, data, person):
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

    def add_relations(self, data, new_person, profile_person):
        profile_relation = data['relation']
        new_relation = get_inverse_relation(profile_relation)

        new_person.relations = [{
            'id': profile_person.id,
            'name': profile_person.name,
            'relation': new_relation
        }]

        to_add = defaultdict(list)

        for relative in profile_person.relations:
            self.add_relations_to_new_person(relative, new_person, profile_relation)
            self.gather_reverse_relations(relative, new_person, profile_relation, to_add)

        new_person.save()
        self.reverse_add_relatives(to_add)

    def add_relations_to_new_person(self, relative, new_person, profile_relation):
        def find_relation():
            if relative['relation'] == 'Parent' and profile_relation == 'Sibling':
                return 'Parent'
            elif relative['relation'] == 'Parent' and profile_relation == 'Parent':
                return 'Spouse'
            elif relative['relation'] == 'Sibling' and profile_relation == 'Parent':
                return 'Child'
            elif relative['relation'] == 'Sibling' and profile_relation == 'Sibling':
                return 'Sibling'
            elif relative['relation'] == 'Child' and profile_relation in 'Child':
                return 'Sibling'
            elif relative['relation'] == 'Child' and profile_relation == 'Spouse':
                return 'Child'
            elif relative['relation'] == 'Spouse' and profile_relation == 'Child':
                return 'Parent'
            else:
                return None

        relation = find_relation()
        if relation:
            new_person.relations.append({**relative, 'relation': relation})

    def gather_reverse_relations(self, relative, new_person, profile_relation, relations_to_add):
        return_object = {'id': new_person.id, 'name': new_person.name}

        def find_relation():
            if relative['relation'] == 'Sibling' and profile_relation == 'Parent':
                return 'Parent'
            elif relative['relation'] == 'Sibling' and profile_relation == 'Sibling':
                return 'Sibling'
            elif relative['relation'] == 'Parent' and profile_relation in 'Sibling':
                return 'Child'
            elif relative['relation'] == 'Parent' and profile_relation == 'Parent':
                return 'Spouse'
            elif relative['relation'] == 'Spouse' and profile_relation == 'Child':
                return 'Child'
            elif relative['relation'] == 'Child' and profile_relation == 'Spouse':
                return 'Parent'
            elif relative['relation'] == 'Child' and profile_relation == 'Child':
                return 'Sibling'
            else:
                return None
        relation = find_relation()
        if relation:
            return_object['relation'] = relation
            relations_to_add[relative['id']].append(return_object)

    def reverse_add_relatives(self, relations):
        person_ids = list(relations.keys())
        persons = Person.objects.filter(id__in=person_ids)

        for person in persons:
            person.relations.extend(relations[person.id])

        Person.objects.bulk_update(persons, ['relations'])
        # for id in relations:
        #     person = Person.objects.get(id=id)
        #     for entry in relations[id]:
        #         person.relations.append(entry)
        #     person.save()

    def add_new_relative_photo(self, data, new_person):
        if 'photo_base64' in data:
            add_photo(new_person.id, True, data['photo_base64'], None)

    def update_profile_person(self, profile_person, new_person, data):
        profile_person.relations.append({
            'id': new_person.id,
            'name': new_person.name,
            'relation': data['relation']
        })
        profile_person.save()


class UpdateDetails(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        profile_data = data.get('profileData')
        person = Person.objects.filter(id=profile_data.get('id')).first()

        self.update_basic_details(person, profile_data)
        self.update_location(person, profile_data)
        self.update_relations(person, profile_data)

        person.save()

        return Response(
            {'message': f'{profile_data['name']} was updated'},
            status=status.HTTP_200_OK
        )

    def update_basic_details(self, person, profile_data):
        for key in ['name', 'birthdate', 'birthplace', 'bio']:
            setattr(person, key, profile_data.get(key))

    def update_location(self, person, profile_data):
        location_name = profile_data.get('location')
        lat, lng = profile_data.get('lat'), profile_data.get('lng')
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

    def update_relations(self, person, profile_data):
        if 'person_add' in profile_data:
            self.add_one_relative(person, profile_data)

        if 'relation_remove' in profile_data:
            self.remove_one_relative(person, profile_data['relation_remove'])

    def add_one_relative(self, person, profile_data):
        new_relative_id = profile_data['person_add']['id']
        new_relative_relation = profile_data['relation_add']['value']

        new_relative_instance = Person.objects.filter(id=new_relative_id).first()

        new_relative = {
            'id': new_relative_id,
            'name': new_relative_instance.name,
            'relation': new_relative_relation
        }
        person.relations.append(new_relative)

        new_relation = get_inverse_relation(new_relative_relation)

        new_relative_instance.relations.append({
            'id': person.id,
            'name': person.name,
            'relation': new_relation
        })
        new_relative_instance.save()

    def remove_one_relative(self, person, id_to_remove):
        def filter_relations(relations, id_to_remove):
            return [relation for relation in relations if relation['id'] != id_to_remove]

        person.relations = filter_relations(person.relations, id_to_remove)

        removed_relative = Person.objects.filter(id=id_to_remove).first()
        removed_relative.relations = filter_relations(removed_relative.relations, person.id)
        removed_relative.save()


class DeleteProfile(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data['profileData']
        person = Person.objects.filter(id=data['id']).first()
        name = person.name

        self.remove_relations(person.relations, person.id)
        self.remove_photos(person)

        person.delete()

        return Response(
            {'message': f'Profile {name} was deleted'},
            status=status.HTTP_200_OK
        )

    def remove_relations(self, relations, id):
        for relation in relations:
            relative = Person.objects.filter(id=relation['id']).first()
            updated_relations = []
            for r in relative.relations:
                if r['id'] != id:
                    updated_relations.append(r)
            relative.relations = updated_relations
            relative.save()

    def remove_photos(self, person):
        photos = person.photos.all()

        for photo in photos:
            photo_path = os.path.join(settings.MEDIA_ROOT, str(photo.file_path))
            if os.path.exists(photo_path):
                os.remove(photo_path)

        person_directory = os.path.join(settings.MEDIA_ROOT, 'photos', str(person.id))
        if os.path.isdir(person_directory) and not os.listdir(person_directory):
            os.rmdir(person_directory)
