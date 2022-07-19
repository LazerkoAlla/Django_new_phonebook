from django.urls import path, re_path

from phonebook import views

app_name = 'phonebook'
urlpatterns = [
    path(r'', views.index, name='index'),
    re_path(r'^([0-9]+)/$', views.details, name='details')

]