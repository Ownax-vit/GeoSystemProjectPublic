from django.contrib.gis import forms
from django.forms import widgets

from .models import *


class ObjectResearchForm(forms.Form):
    error_css_class = 'alert alert-danger'
    id = forms.IntegerField(required=False)
    name = forms.CharField(max_length=255)
    description = forms.CharField( widget=forms.Textarea)
    author = forms.CharField(required=False)
    date_create = forms.DateTimeField(required=False)

    # при инициализации формы даем ему атрибут класса bootstrap
    # и дополнительные атрибуты полей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['author'].widget.attrs['readonly'] = True
        self.fields['author'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['date_create'].widget.attrs['readonly'] = True
        self.fields['date_create'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['id'].widget.attrs['readonly'] = True
        self.fields['id'].widget.attrs['class'] = 'form-control-plaintext'


class ObjectBussinessForm(forms.Form):

    error_css_class = 'alert alert-danger'
    id = forms.IntegerField(required=False)
    author = forms.CharField(required=False)
    date = forms.DateTimeField(required=False)
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    rent_price = forms.FloatField()
    area = forms.FloatField()
    pop = forms.FloatField()
    dist_of_ind = forms.FloatField()
    source = forms.URLField(required=False)
    lat = forms.FloatField(required=False)
    long = forms.FloatField(required=False)
    radius = forms.FloatField(required=False)
    geom = forms.PointField(widget=forms.OSMWidget({'map_width': 600, 'map_height': 400,
                                                    'default_lat': 50.5984208008572,
                                                    'default_lon': 36.58824921758033,
                                                    # 'display_raw': True, # окно дебагга
                                                    'default_zoom': 13,
                                                    },

                                                   ),
                            required=False)

    circle = forms.PolygonField(widget=forms.OSMWidget({
                                                        # 'map_width': 80, 'map_height': 400,
                                                        'default_lat': 50.5984208008572,
                                                        'default_lon': 36.58824921758033,
                                                        # 'display_raw': True,
                                                        'default_zoom': 13,
                                                        'disabled': True,
                                                        }),
                                required=False)

    def clean(self):
        super().clean()
        lat = self.cleaned_data.get('lat')
        long = self.cleaned_data.get('long')
        if long and lat:
            if lat < -180.0 or lat > 180.0:
                self._errors['lat'] = self.error_class([
                    'Широта задана неверно! '])
            if long < -180.0 or long > 180.0:
                self._errors['long'] = self.error_class([
                    'Долгота задана неверно!'])


        return self.cleaned_data

    # required делает необязательном заполнение поля, важно
    # при проверке валидации создания объектов

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control rounded-start'
        self.fields['author'].widget.attrs['readonly'] = True
        self.fields['author'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['date'].widget.attrs['readonly'] = True
        self.fields['date'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['radius'].widget.attrs['readonly'] = True
        self.fields['radius'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['circle'].widget.attrs['readonly'] = True
        self.fields['circle'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['id'].widget.attrs['readonly'] = True
        self.fields['id'].widget.attrs['class'] = 'form-control-plaintext'


class ObjectInfrastructureForm(forms.Form):
    error_css_class = 'alert alert-danger'
    id = forms.IntegerField(required=False)
    author = forms.CharField(required=False)
    date = forms.DateTimeField(required=False)
    name = forms.CharField(max_length=100)
    address = forms.CharField(max_length=255)
    lat = forms.FloatField(required=False)
    long = forms.FloatField(required=False)
    radius = forms.FloatField()
    geom = forms.PointField(widget=forms.OSMWidget({'map_width': 600, 'map_height': 400,
                                                    'default_lat': 50.5984208008572,
                                                    'default_lon': 36.58824921758033,
                                                    # 'display_raw': True, # окно дебагга
                                                    'default_zoom': 13,
                                                    }
                                                   ),
                            required=False)

    circle = forms.PolygonField(widget=forms.OSMWidget({'map_width': 600, 'map_height': 400,
                                                        'default_lat': 50.5984208008572,
                                                        'default_lon': 36.58824921758033,
                                                        # 'display_raw': True,
                                                        'default_zoom': 13,
                                                        'disabled': True,}),
                                required=False)
    # required делает необязательном заполнение поля, важно
    # при проверке валидации создания объектов

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control rounded-start'
        self.fields['author'].widget.attrs['readonly'] = True
        self.fields['author'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['date'].widget.attrs['readonly'] = True
        self.fields['date'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['circle'].widget.attrs['readonly'] = True
        self.fields['circle'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['id'].widget.attrs['readonly'] = True
        self.fields['id'].widget.attrs['class'] = 'form-control-plaintext'

    def clean(self):
        super().clean()
        lat = self.cleaned_data.get('lat')
        long = self.cleaned_data.get('long')
        if long and lat:
            if lat < -180.0 or lat > 180.0:
                self._errors['lat'] = self.error_class([
                    'Широта задана неверно! '])
            if long < -180.0 or long > 180.0:
                self._errors['long'] = self.error_class([
                    'Долгота задана неверно!'])

        return self.cleaned_data


class FormViewIntersectionObject(forms.Form):
    obj_business = forms.IntegerField()
    obj_infrastructure = forms.IntegerField()
    geom = forms.PolygonField(widget=forms.OSMWidget({'map_width': 600, 'map_height': 400,
                                                    'default_lat': 50.5984208008572,
                                                    'default_lon': 36.58824921758033,
                                                    #'display_raw': True,
                                                    'default_zoom': 13,
                                                    'disabled': True,}
                                                    ),

                              required=False)
    area = forms.FloatField(label='Площадь:')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control rounded-start'
            self.fields[field].widget.attrs['readonly'] = True
            self.fields[field].widget.attrs['class'] = 'form-control-plaintext'


class ImportInfrastructureForm(forms.Form):
    id_researchFromImport = forms.ModelChoiceField(queryset=ObjectResearch.objects.all(),
                                                   label='Выберите объект исследования:')
