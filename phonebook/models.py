from django.db import models

# Create your models here.
class Name(models.Model):
    person_name = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')

class Detail(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)