from django.db import models
# встроенная модель пользователя
# нужна для авторов сообщений
from django.contrib.auth.models import User
# тип "временнАя зона" для получения текущего времени
from django.utils import timezone

# Create your models here.
class Name(models.Model):
    person_name = models.CharField(max_length=255)
    pub_date = models.DateTimeField('date published')

class Detail(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

class Message(models.Model):
    chat = models.ForeignKey(
        Name,
        verbose_name='Чат под именем',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        User,
        verbose_name='Пользователь', on_delete=models.CASCADE)
    message = models.TextField('Сообщение')
    pub_date = models.DateTimeField(
        'Дата сообщения',
        default=timezone.now)

# class Mark(models.Model):
#     name = models.ForeignKey(
#         Name,
#         verbose_name='Загадка',
#         on_delete=models.CASCADE)
#     author = models.ForeignKey(
#         User,
#         verbose_name='Пользователь', on_delete=models.CASCADE)
#     mark = models.IntegerField(
#         verbose_name='Оценка')
#     pub_date = models.DateTimeField(
#         'Дата оценки',
#         default=timezone.now)

# class Mark(models.Model):
#     name = models.ForeignKey(
#         Name,
#         verbose_name='Загадка',
#         on_delete=models.CASCADE)
#     author = models.ForeignKey(
#     User,
#         verbose_name='Пользователь', on_delete=models.CASCADE)
#     mark = models.IntegerField(
#         verbose_name='Оценка')
#     pub_date = models.DateTimeField(
#         'Дата оценки',
#         default=timezone.now)

