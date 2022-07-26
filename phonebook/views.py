from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
# главная страница со списком телефонов
from phonebook.models import Name, Detail, Mark

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

from django import forms
from django.utils.translation import gettext, gettext_lazy as _
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
            "already_rated_by_user":
                Mark.objects
                    .filter(author_id=request.user.id)
                    .filter(name=id)
                    .count(),

            # # оценка текущего пользователя
            "user_rating":
                Mark.objects
                    .filter(author_id=request.user.id)
                    .filter(name=id)
                    .aggregate(Avg('mark'))
                ["mark__avg"],

            # # средняя по всем пользователям оценка
            "avg_mark":
                Mark.objects
                    .filter(name=id)
                    .aggregate(Avg('mark'))
                ["mark__avg"]
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



def post_mark(request, id):
    msg = Mark()
    msg.author = request.user
    msg.name = get_object_or_404(Name, pk=id)
    msg.mark = request.POST['mark']
    msg.pub_date = datetime.now()
    msg.save()
    return HttpResponseRedirect(app_url + str(id))

def get_mark(request, id):
    res = Mark.objects\
    .filter(name_id=id)\
    .aggregate(Avg('mark'))
    return JsonResponse(json.dumps(res), safe=False)

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

def admin(request):
    message = None
    if "message" in request.GET:
        message = request.GET["message"]
# создание HTML-страницы по шаблону admin.html
# с заданными параметрами latest_riddles и message
    return render(
        request,
        "admin.html",
        {
            "latest_riddles":
            Name.objects.order_by('-pub_date')[:5],
            "message": message,
        }
    )

def post_riddle(request):
# защита от добавления загадок неадминистраторами
    author = request.user
    if not (author.is_authenticated and author.is_staff):
        return HttpResponseRedirect(app_url+"admin")
# добавление загадки
    rid = Name()
    rid.person_name = request.POST['text']
    rid.pub_date = datetime.now()
    rid.save()
# добавление вариантов ответа
    i = 1 # нумерация вариантов на форме начинается с 1
# количество вариантов неизвестно,
# поэтому ожидаем возникновение исключения,
# когда варианты кончатся
    try:
        while request.POST['option'+str(i)]:
            opt = Detail()
            opt.name = rid
            opt.phone = request.POST['option'+str(i)]
            opt.email = request.POST['option' + str(i)]
            opt.save()

# это ожидаемое исключение,
# при котором ничего делать не надо
    except:
        pass
        return HttpResponseRedirect(app_url+str(rid.id))

        # цикл по всем пользователям
    for i in User.objects.all():
            # проверка, что текущий пользователь подписан - указал e-mail
        if i.email != '':
            send_mail(
                    # тема письма
                'New riddle',
                    # текст письма
                'A new riddle was added on riddles portal:\n' +
                'http://localhost:8000/riddles/' + str(rid.id) + '.',
                    # отправитель
                'lazerko.alla@bk.ru',
                    # список получателей из одного получателя
                [i.email],
                    # отключаем замалчивание ошибок,
                    # чтобы из видеть и исправлять
                False
                )
    return HttpResponseRedirect(app_url + str(rid.id))


class SubscribeForm(forms.Form):
# поле для ввода e-mail
    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
    )
# конструктор для запоминания пользователя,
# которому задается e-mail
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
# сохранение e-mail
    def save(self, commit=True):
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
        return self.user

# класс, описывающий взаимодействие логики
# со страницами веб-приложения
class SubscribeView(FormView):
# используем класс с логикой
    form_class = SubscribeForm
# используем собственный шаблон
    template_name = 'subscribe.html'
# после подписки возвращаем на главную станицу
    success_url = app_url
# передача пользователя для конструктора класса с логикой
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
# вызов логики сохранения введенных данных
    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.success_url)

def unsubscribe(request):
    request.user.email = ''
    request.user.save()
    return HttpResponseRedirect(app_url)

