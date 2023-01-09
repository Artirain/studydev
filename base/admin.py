from django.contrib import admin

# Register your models here.

from . models import Room, Topic, Message #импортируем класс Room из моделей

admin.site.register(Room)    #регистрируем наше приложение
admin.site.register(Topic)   #регистрируем наше приложение
admin.site.register(Message) #регистрируем наше приложение