from collections import defaultdict
from .models import Person, Location


def create_new_relative(data):
    person = Person.objects.create(
        name=data.get('name'),
        birthdate=data.get('birthdate'),
        birthplace=data.get('birthplace'),
        bio=data.get('bio'),
    )

    location_name = data.get('location')
    if location_name:
        Location.objects.create(
            person=person,
            name=location_name,
            lat=data.get('lat'),
            lng=data.get('lng')
        )

    return person


def add_relations(data, new_relative, profile_person):
    def get_inverse_relation(relation):
        if relation == 'Parent':
            return 'Child'
        elif relation == 'Child':
            return 'Parent'
        else:
            return relation

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
        elif relative_relation == 'Sibling' and profile_relation in ['Parent', 'Sibling']:
            new_relations.append(
                create_relation_entry(
                    relative, 'Child' if profile_relation == 'Parent' else 'Sibling'
                )
            )
        elif relative_relation == 'Child' and profile_relation in ['Child', 'Spouse']:
            new_relations.append(
                create_relation_entry(
                    relative, 'Sibling' if profile_relation == 'Child' else 'Parent'
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
        elif relative_relation == 'Parent' and profile_relation == 'Sibling':
            relations_to_add[relative['id']].append(
                create_relation_entry(
                    {'id': new_relative.id, 'name': new_relative.name}, 'Child'
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
