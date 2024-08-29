from .models import Person


def create_new_relative(data, profile_person):
    relation = data.get('relation')
    name = data.get('name')

    return Person.objects.create(
        name=data.get('name'),
        birthdate=data.get('birthdate'),
        birthplace=data.get('birthplace'),
        bio=data.get('bio'),
        relations=relations_for_new_relative(relation, profile_person, name)
    )


def relations_for_new_relative(relation, profile_person, name):
    new_relations = []
    new_relation = None
    if relation == 'Sibling' or relation == 'Spouse':
        new_relation = relation
    elif relation == 'Parent':
        new_relation = 'Child'
    else:
        new_relation = 'Parent'

    new_relations.append({
        'id': profile_person.id,
        'relation': new_relation,
        'name': profile_person.name
    })

    for person in profile_person.relations:
        if relation == 'Sibling' and person['relation'] == 'Sibling':
            new_relations.append(person)

    return new_relations


def add_to_profile_relations(new_person, data):
    return {
        'id': new_person.id,
        'relation': data.get('relation'),
        'name': new_person.name
    }
