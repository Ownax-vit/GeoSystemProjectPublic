from django.contrib.gis import admin
from django.contrib.gis.admin import GeoModelAdmin

from .models import *


# Register your models here.
@admin.register(ObjectBusiness)
class ObjectBusinessAdmin(admin.OSMGeoAdmin):
    list_display = ('id', 'name', 'date',   'obj_research')
    list_filter = ('id', 'name', 'date',  'obj_research')


@admin.register(ObjectInfrastructure)
class ObjectInfrastructureAdmin(admin.OSMGeoAdmin):
    list_display = ('id', 'name', 'date',  'radius')
    list_filter = ('id', 'name', 'date', 'radius')


@admin.register(ObjectResearch)
class ObjectResearchAdmin(admin.OSMGeoAdmin):
    list_display = ('id', 'name', 'date_create', 'author')
    list_filter = ('id', 'name', 'date_create',  'author')


@admin.register(ObjectIntersections)
class ObjectIntersectionsAdmin(admin.OSMGeoAdmin):
    list_display = ('id', 'obj_business', 'obj_infrastructure',  'area')
    list_filter = ('id', 'obj_business', 'obj_infrastructure', 'area')

