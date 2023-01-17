from django.forms import ModelForm
from . models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__' #забираем все поля наших моделей
        exclude = ['host', 'participants'] #исключили эти поля