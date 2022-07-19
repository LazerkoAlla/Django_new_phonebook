from django.contrib import admin

# Register your models here.
from phonebook.models import Name, Detail

admin.site.register(Name)
admin.site.register(Detail)
