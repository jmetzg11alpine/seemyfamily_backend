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
    new_relations = []
    relations_to_add = []
    temp_relation = None
    profile_relation = data['relation']

    def handle_relations_to_add(relative, relation):
        relations_to_add.append({
            'profile_id': relative['id'],
            'id': new_relative.id,
            'name': new_relative.name,
            'relation': relation
        })

    # adding the relative of the profile person
    if profile_relation == 'Spouse' or profile_relation == 'Sibling':
        temp_relation = data['relation']
    elif profile_relation == 'Parent':
        temp_relation = 'Child'
    else:
        temp_relation = 'Parent'

    new_relations.append({
        'id': profile_person.id,
        'name': profile_person.name,
        'relation': temp_relation
    })

    # profile person's relatives
    for relative in profile_person.relations:
        temp_relation = relative['relation']

        if temp_relation == 'Parent' and profile_relation == 'Sibling':
            new_relations.append(relative)
            handle_relations_to_add(relative, 'Sibling')

        elif temp_relation == 'Sibling':
            if profile_relation == 'Parent':
                relative['relation'] = 'Child'
                new_relations.append(relative)
                handle_relations_to_add(relative, '')

            if profile_relation == 'Sibling':
                new_relations.append(relative)
                handle_relations_to_add(relative, '')

        elif temp_relation == 'Child':
            if profile_relation == 'Child':
                relative['relation'] = 'Sibling'
                new_relations.append(relative)
                handle_relations_to_add(relative, '')

            if profile_relation == 'Spouse':
                new_relations.append(relative)
                handle_relations_to_add(relative, '')

        elif temp_relation == 'Spouse' and profile_relation == 'Child':
            relative['relation'] = 'Parent'
            new_relations.append(relative)
            handle_relations_to_add(relative, '')

    new_relative.relations = new_relations
    new_relative.save()

    reverse_add_relatives(relations_to_add)


def reverse_add_relatives(relations):
    print(relations)
