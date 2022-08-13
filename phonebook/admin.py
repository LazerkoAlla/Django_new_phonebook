from django.contrib import admin

# Register your models here.
from phonebook.models import Name, Detail
from .models import Message
# from .models import Mark



admin.site.register(Name)
admin.site.register(Detail)


admin.site.register(Message)
# admin.site.register(Mark)
