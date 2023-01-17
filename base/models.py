from django.db import models
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Room(models.Model):
    host =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True) #посты останутся в БД даже при удалении автора, но значение в поле author у постов изменится на None
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #это поле может быть пустым в бд, эта форма так же может быть пуста при отправке
    participants = models.ManyToManyField(User, related_name='participants', blank=True)               #участники
    updated = models.DateTimeField(auto_now=True) #auto_now обновляет дату каждый раз при изменении (сохранении) строки в базе;
    created = models.DateTimeField(auto_now_add=True) #auto_now_add создает дату при создании строки в базе данных

    class Meta:
        ordering = ['-updated', '-created']#атрибут ordering - сортирует по убыванию по created_at 

    #Это переопределяет имя объектов этого класса по умолчанию, 
    #Переопределение дает более удобное для человека имя объекта, пр. как Author.name
    def __str__(self):
        return self.name 

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)       #пользователь который отправляет сообщение
    #cвязь один ко многим
    room = models.ForeignKey(Room, on_delete=models.CASCADE) #если комната будет удалена, то все сообщения будут тоже удалены
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) #auto_now обновляет дату каждый раз при изменении (сохранении) строки в базе;
    created = models.DateTimeField(auto_now_add=True) #auto_now_add создает дату при создании строки в базе данных

    class Meta:
        ordering = ['-updated', '-created'] #атрибут ordering - сортирует по убыванию по created_at 

    def __str__(self):
        return self.body[0:50] #обрезаем до первых 50 символов