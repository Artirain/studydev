from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from . models import Room, Topic, Message
from . forms import RoomForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated: #если пользователь авторизован
        return redirect('home')       #возвращаем его на главную страницу

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        #проверка на пользователя, существует ли он
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist') #сообщение об ошибке "Пользователь не существует"
        
        #как только у нас появится пользователь, его нужно аутентифицировать
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist") #Имя пользователя или пароль не существует

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

#функция для выхода
def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm() #создание формы регистрации

    if request.method == 'POST': #мы передаем данные пользователя
        form = UserCreationForm(request.POST) #мы бросаем это в форму создание пользователя
        if form.is_valid(): #мы проверяем, действительна ли форма
            user = form.save(commit=False) #если это так, мы получаем имя пользователя
            user.username = user.username.lower() #получаем имя пользователя в нижнем регистре.
            user.save()  #сохраняем пользователя
            login(request, user) #регистрируем пользователя

            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration') #При регистрации произошла ошибка

    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) #обращаемся к родителию Topic и забираем name, icontains = поиск по буквам

    topics = Topic.objects.all()
    room_count =  rooms.count() #получаем длину набора запросов
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create( #Для добавления данных применяется метод create():
            user = request.user,
            room = room,
            body = request.POST.get('body') #получаем запись body из бд
        )

        room.participants.add(request.user) #пользователь будет добавлен по отношению многие ко многим (будет виден во вкладки Participants)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 
                'participants': participants}

    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk) #получаем все объекты связанные с пользователем
    rooms = user.room_set.all() #связываем всех пользователей с комнатой
    room_messages = user.message_set.all() 
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
            'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login') #перенаправляем пользователя на страницу входа, если он не зарегестрирован или не залогинелся
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False) #мы пока не хотим сохранять модель Post — сначала нужно добавить автора
        #     room.host = request.user
        #     room.save()
        return redirect('home') #перенаправление на домашнюю страницу


    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') #перенаправляем пользователя на страницу входа, если он не зарегестрирован или не залогинелся
def updateRoom(request, pk):
    room = Room.objects.get(id=pk) #собираемся получить значение по pk
    form = RoomForm(instance=room) #сначала получаем room, затем получаем форму
                                   #эта форма будет предварительно заполнена room
    topics = Topic.objects.all()
    if request.user != room.host: #Если ты не владелец комнаты
        return HttpResponse('You are not allowed here') #то будет отправлено сообщение('Тебе нельзя здесь')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login') #перенаправляем пользователя на страницу входа, если он не зарегестрирован или не залогинелся
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host: #Если ты не владелец комнаты
        return HttpResponse('You are not allowed here') #то будет отправлено сообщение('Тебе нельзя здесь')

    if request.method == 'POST':
        room.delete()  #удаление комнаты
        return redirect('home')

    return render(request, 'base/delete.html', {'obj' : room})


@login_required(login_url='login') #перенаправляем пользователя на страницу входа, если он не зарегестрирован или не залогинелся
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user: #Если ты не владелец сообщения
        return HttpResponse('You are not allowed here') #то будет отправлено сообщение('Тебе нельзя здесь')

    if request.method == 'POST':
        message.delete()  #удаление сообщения
        return redirect('home')

    return render(request, 'base/delete.html', {'obj' : message})


@login_required(login_url='login')   
def updateUser(request):
    return render(request, 'base/update-user.html')
