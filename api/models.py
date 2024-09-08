from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=255, unique=True)
    birthdate = models.DateField(max_length=255, blank=True, null=True)
    birthplace = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    relations = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    person = models.ForeignKey(Person, related_name='location', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.lat}, {self.lng})"


class Photo(models.Model):
    person = models.ForeignKey(Person, related_name='photos', on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.ImageField(upload_to='photos/', blank=True, null=True)
    profile_pic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.description} ({'Profile Pic' if self.profile_pic else 'Photo'})"

    def save(self, *args, **kwargs):
        if self.profile_pic:
            Photo.objects.filter(person=self.person, profile_pic=True).update(profile_pic=False)
        super().save(*args, **kwargs)
