from django.urls import path
from . views import *


urlpatterns = [
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),
    path('register/', registerPage, name='register'),

    path('', home, name='home'), #домашнаяя страницы
    path('room/<str:pk>/', room, name='room'), #комната

    path('create-room/', createRoom, name='create-room'),  #создание комнаты
    path('update-room/<str:pk>', updateRoom, name='update-room'), #обновление комнаты
    path('delete-room/<str:pk>', deleteRoom, name='delete-room')  #удаление комнаты
]
