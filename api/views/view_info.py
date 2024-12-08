from django.http import FileResponse
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
import zipfile
from ..models import History, Visitor, Location, Photo
from datetime import timedelta, datetime
import tempfile
import subprocess
import os


@api_view(['POST'])
def get_edits(request):
    data = History.objects.all().order_by('-created_at')

    history_data = [
        {
            'id': item.id,
            'created_at': item.created_at,
            'username': item.username,
            'action': item.action,
            'recipient': item.recipient
        } for item in data
    ]
    return Response({'data': history_data})


@api_view(['POST'])
def get_visitors(request):
    data = request.data

    if data == 'week':
        days_ago = 7
        group_size = 1
    elif data == 'month':
        days_ago = 30
        group_size = 5
    else:
        days_ago = 180
        group_size = 30

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days_ago)
    delta = timedelta(days=group_size)

    visitors = Visitor.objects.filter(date__gte=start_date).values('date').order_by('date')

    group_data = {}
    temp_start = start_date
    while temp_start <= end_date:
        group_data[temp_start] = 0
        temp_start += delta

    count = 0
    temp_start = start_date
    for visitor in visitors:
        curr_date = visitor['date']

        while curr_date >= temp_start + delta:
            group_data[temp_start] = count
            count = 0
            temp_start += delta
        count += 1
    group_data[curr_date] = count

    lables = [key for key in group_data]
    data = [value for _, value in group_data.items()]
    return Response(
        {
            'data': {
                'labels': lables,
                'data': data
            }
        }
    )


@api_view(['POST'])
def get_geo_data(request):
    locations = Location.objects.all()

    data = {}
    for location in locations:
        if location.lat and location.lng:
            lat_lng = str(location.lat) + '-' + str(location.lng)
            if lat_lng in data:
                data[lat_lng]['person'].append(location.person.name)
                data[lat_lng]['size'] += 1
            else:
                data[lat_lng] = {
                    'id': location.id,
                    'name': location.name,
                    'person': [location.person.name],
                    'lat': location.lat,
                    'lng': location.lng,
                    'size': 1
                }

    data = [value for _, value in data.items()]

    return Response({
        'data': data
    })


@api_view(['POST'])
def download_sql(request):
    MODE = os.getenv('MODE')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".sql") as temp_file:
        temp_file_path = temp_file.name

    USER = os.getenv(f'{MODE}_POSTGRES_USER')
    PASS = os.getenv(f'{MODE}_POSTGRES_PASSWORD')
    HOST = os.getenv(f'{MODE}_POSTGRES_HOST')
    NAME = os.getenv(f'{MODE}_POSTGRES_NAME')
    FILE_NAME = 'seemyfamil_' + datetime.now().strftime('%Y-%m-%d') + '.sql'

    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = PASS

        command = [
            "pg_dump",
            "-U", USER,
            "-h", HOST,
            "-d", NAME,
            "-F", "p",
            "-t", "api_history",
            "-t", "api_location",
            "-t", "api_person",
            "-t", "api_photo",
            "-t", "api_visitor",
            "-f", temp_file_path
        ]

        subprocess.run(command, env=env, check=True)

        response = FileResponse(
            open(temp_file_path, 'rb'),
            as_attachment=True,
            filename=FILE_NAME
        )
        print(response)
        return response

    except Exception as e:
        print(f'Could not download sql: {e}')
        return Response({'message': f'Could not download sql: {e}'})

def make_readable_path(photo):
    ending = photo['path'].split('.')[-1]
    if photo['description']:
        path = photo['name'] + '/' + photo['description'] + '.' + ending
    else:
        unique_numbers = photo['path'].split('.')[-2]
        path = photo['name'] + '/' + unique_numbers + '.' + ending
    return path

@api_view(['POST'])
def download_photos(request):
    all_photos = [
        {
            'path': photo.file_path.name,
            'description': photo.description,
            'name': photo.person.name
        }
        for photo in Photo.objects.all()
    ]

    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
        with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
            for photo in all_photos:
                full_path = settings.MEDIA_ROOT + '/' + photo['path']
                relative_path = make_readable_path(photo)
                zipf.write(full_path, arcname=relative_path)
    temp_zip_path = temp_zip.name
    return FileResponse(
        open(temp_zip_path, 'rb'),
        as_attachment=True,
        filename='photos_zio'
    )
    # return Response({'message': 'hello'})

