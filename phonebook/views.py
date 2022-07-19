from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
# главная страница со списком телефонов
from phonebook.models import Name, Detail


def index(request):
    message = None
    if "message" in request.GET:
        message = request.GET["message"]
    # создание HTML-страницы по шаблону index.html
    # с заданными параметрами latest_riddles и message
    return render(
        request,
        "index.html",
        {
            "latest_names":
                Name.objects.order_by('-pub_date')[:5],
            "message": message
        }
    )
# страница загадки со списком ответов
def details(request, name_id):
    error_message = None
    if "error_message" in request.GET:
        error_message = request.GET["error_message"]
    return render(
        request,
        "details.html",
        {
            "name": get_object_or_404(Name, pk=name_id),
            "error_message": error_message
        }
    )