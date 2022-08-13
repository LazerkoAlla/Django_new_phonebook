from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
# главная страница со списком телефонов
from phonebook.models import Name, Detail

# Базовый класс для обработки страниц с формами.
from django.views.generic.edit import FormView
# Спасибо django за готовую форму регистрации.
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
# Функция для установки сессионного ключа.
# По нему django будет определять,
# выполнил ли вход пользователь.
from django.contrib.auth import login

# Для Log out с перенаправлением на главную
from django.http import HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth import logout

# Для смены пароля - форма
from django.contrib.auth.forms import PasswordChangeForm

from .models import Message
from datetime import datetime

from django.http import JsonResponse
import json


# вычисление среднего,
# например, средней оценки
from django.db.models import Avg

app_url = "/phonebook/"

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
# страница загадки со списком ответов !!!!!!!!!!!!!!!!!!!!!!!!1
# def details (request, name_id):
#     error_message = None
#     if "error_message" in request.GET:
#         error_message = request.GET["error_message"]
#     return render(
#         request,
#         "details.html",
#         {
#             "name": get_object_or_404(Name, pk=name_id),
#             "error_message": error_message
#         }
#     )
def detail(request, id):
    error_message = None
    if "error_message" in request.GET:
        error_message = request.GET["error_message"]
    return render(
        request,
        "details.html",
        {
            "name": get_object_or_404(
                Name, pk=id),
            "error_message": error_message,
            "latest_messages":
                Message.objects
                    .filter(chat_id=id)
                    .order_by('-pub_date')[:5],

            # # кол-во оценок, выставленных пользователем
            # "already_rated_by_user":
            #     Mark.objects
            #         .filter(author_id=request.user.id)
            #         .filter(name=id)
            #         .count(),
            #
            # # оценка текущего пользователя
            # "user_rating":
            #     Mark.objects
            #         .filter(author_id=request.user.id)
            #         .filter(name=id)
            #         .aggregate(Avg('mark'))
            #     ["mark__avg"],
            #
            # # средняя по всем пользователям оценка
            # "avg_mark":
            #     Mark.objects
            #         .filter(name=id)
            #         .aggregate(Avg('mark'))
            #     ["mark__avg"]
        }
    )
# наше представление для регистрации
class RegisterFormView(FormView):
# будем строить на основе
# встроенной в django формы регистрации
    form_class = UserCreationForm
# Ссылка, на которую будет перенаправляться пользователь
# в случае успешной регистрации.
# В данном случае указана ссылка на
# страницу входа для зарегистрированных пользователей.
    success_url = app_url + "login/"
# Шаблон, который будет использоваться
# при отображении представления.
    template_name = "reg/register.html"
    def form_valid(self, form):
# Создаём пользователя,
# если данные в форму были введены корректно.
        form.save()
# Вызываем метод базового класса
        return super(RegisterFormView, self).form_valid(form)


# наше представление для входа
class LoginFormView(FormView):
# будем строить на основе
# встроенной в django формы входа
    form_class = AuthenticationForm
# Аналогично регистрации,
# только используем шаблон аутентификации.
    template_name = "reg/login.html"
# В случае успеха перенаправим на главную.
    success_url = app_url
    def form_valid(self, form):
# Получаем объект пользователя
# на основе введённых в форму данных.
        self.user = form.get_user()
# Выполняем аутентификацию пользователя.
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


# для выхода - миниатюрное представление без шаблона -
# после выхода перенаправим на главную
class LogoutView(View):
    def get(self, request):
# Выполняем выход для пользователя,
# запросившего данное представление.
        logout(request)
# После чего перенаправляем пользователя на
# главную страницу.
        return HttpResponseRedirect(app_url)

# наше представление для смены пароля
class PasswordChangeView(FormView):
# будем строить на основе
# встроенной в django формы смены пароля
    form_class = PasswordChangeForm
    template_name = 'reg/password_change_form.html'
# после смены пароля нужно снова входить
    success_url = app_url + 'login/'
    def get_form_kwargs(self):
        kwargs = super(PasswordChangeView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs
    def form_valid(self, form):
        form.save()
        return super(PasswordChangeView, self).form_valid(form)


# def post_mark(request, id):
#     msg = Mark()
#     msg.author = request.user
#     msg.name = get_object_or_404(Name, pk=id)
#     msg.mark = request.POST['mark']
#     msg.pub_date = datetime.now()
#     msg.save()
#     return HttpResponseRedirect(app_url + str(id))
#
# def get_mark(request, id):
#     res = Mark.objects\
#     .filter(name_id=id)\
#     .aggregate(Avg('mark'))
#     return JsonResponse(json.dumps(res), safe=False)

def msg_list(request, name_id):
    # выбираем список сообщений
    res = list(
        Message.objects
            # фильтруем по id загадки
            .filter(chat_id=name_id)
            # отбираем 5 самых свежих
            .order_by('-pub_date')[:5]
            # выбираем необходимые поля
            .values('author__username',
                    'pub_date',
                    'message'
                    )
    )
    # конвертируем даты в строки - сами они не умеют
    for r in res:
        r['pub_date'] = \
            r['pub_date'].strftime(
                '%d.%m.%Y %H:%M:%S'
            )
    return JsonResponse(json.dumps(res), safe=False)

def post(request, riddle_id):
    msg = Message()
    msg.author = request.user
    msg.chat = get_object_or_404(Name, pk=riddle_id)
    msg.message = request.POST['message']
    msg.pub_date = datetime.now()
    msg.save()
    return HttpResponseRedirect(app_url+str(riddle_id))

# def post_mark(request, name_id):
#     msg = Mark()
#     msg.author = request.user
#     msg.name = get_object_or_404(Name, pk=name_id)
#     msg.mark = request.POST['mark']
#     msg.pub_date = datetime.now()
#     msg.save()
#     return HttpResponseRedirect(app_url+str(name_id))
#
# def get_mark(request, name_id):
#     res = Mark.objects.filter(name_id=name_id).aggregate(Avg('mark'))
#     return JsonResponse(json.dumps(res), safe=False)


