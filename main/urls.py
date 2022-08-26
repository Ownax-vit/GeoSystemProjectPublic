from django.urls import re_path
from .views import *

urlpatterns = [

    re_path(r'^$', indexList, name='index-page'),
    re_path(r'^createObjectResearch$', createObjectResearch, name='create_objectResearch-page'),
    re_path(r'^editObjectResearch/(?P<objectResearch_id>\d+)$', editObjectResearch,
        name='edit_objectResearch-page'),
    re_path(r'^deleteObjectResearch/(?P<objectResearch_id>\d+)$', deleteObjectResearch,
        name='delete_objectResearch-page'),

    re_path(r'^workingObjectResearch/(?P<objectResearch_id>\d+)$', working_ObjectResearch,
        name='working_ObjectResearch-page'),

    re_path(r'editObjectBusiness/(?P<objectResearch_id>\d+)/(?P<objectBusiness_id>\d+)$', editObjectBusiness,
        name='edit_ObjectBusiness-page'),
    re_path(r'createObjectBusiness/(?P<objectResearch_id>\d+)$', editObjectBusiness,
        name='create_ObjectBusiness-page'),
    re_path(r'deleteObjectBusiness/(?P<objectBusiness_id>\d+)$', deleteObjectBusiness,
        name='delete_ObjectBusiness'),

    re_path(r'objectsBusiness/(?P<objectResearch_id>\d+)$', allObjectsBusiness,
        name='all_ObjectsBusiness-page'),

    re_path(r'^edit_objectInfrastructure/(?P<objectResearch_id>\d+)/(?P<objectInfrastructure_id>\d+)$',
        editObjectInfrastructure, name='edit_ObjectInfrastructure-page'),
    re_path(r'^create_objectInfrastructure/(?P<objectResearch_id>\d+)', createObjectInfrastructure,
        name='create_ObjectInfrastructure-page'),
    re_path(r'deleteObjectInfrastructure/(?P<objectResearch_id>\d+)/(?P<objectInfrastructure_id>\d+)$',
        deleteObjectInfrastructure, name='delete_ObjectInfrastructure'),
    re_path(r'objectsInfrastructure/(?P<objectResearch_id>\d+)$', allObjectInfrastructure,
        name='all_ObjectsInfrastructure-page'),

    re_path(r'^calc_objectsIntersections/(?P<objectResearch_id>\d+)$', calc_objectIntersections,
        name='calc_ObjectsIntersections'),
    re_path(r'objectsIntersections/(?P<objectResearch_id>\d+)$', allObjectIntersections,
        name='all_ObjectsIntersections-page'),
    re_path(r'^view_objectIntersections/(?P<objectIntersections_id>\d+)$',
        view_objectIntersections, name='view_ObjectIntersections-page'),

    re_path(r'^all_objectBusinessRanging/(?P<objectResearch_id>\d+)$',
        allObjectBusinessRanging, name='all_ObjectBusinessRange-page'),


    # -------- Экспорт -----------
    re_path(r'^exportObjectsBusinessXLX/(?P<objectResearch_id>\d+)$', export_business_xls,
        name='exportXLX_ObjectsBusiness'),
    re_path(r'^exportObjectsBusinessCSV/(?P<objectResearch_id>\d+)$', export_business_csv,
        name='exportCSV_ObjectsBusiness'),

    re_path(r'^exportObjectsInfrastructureXLX/(?P<objectResearch_id>\d+)$', export_infrastructure_xls,
            name='exportXLX_ObjectsInfrastructure'),
    re_path(r'^exportObjectsInfrastructureCSV/(?P<objectResearch_id>\d+)$', export_infrastructure_csv,
            name='exportCSV_ObjectsInfrastructure'),


    re_path(r'^exportObjectsBusinessRangXLX/(?P<objectResearch_id>\d+)$', export_objectsBusinessRang_xls,
            name='exportXLX_ObjectsBusinessRang'),
    re_path(r'^exportObjectsBusinessRangCSV/(?P<objectResearch_id>\d+)$', export_objectsBusinessRang_csv,
                name='exportCSV_ObjectsBusinessRang'),


    re_path(r'object_business_dataset/(?P<objectResearch_id>\d+)$', objects_business_dataset,
        name='object_business_dataset' ),
    re_path(r'object_infrastructure_dataset/(?P<objectResearch_id>\d+)$', objects_infrastructure_dataset,
        name='object_infrastructure_dataset'),

    re_path(r'object_businessCircle_dataset/(?P<objectResearch_id>\d+)$', objects_business_circle_dataset,
        name='object_businessCircle_dataset'),

    re_path(r'object_infrastructureCircle_dataset/(?P<objectResearch_id>\d+)$', objects_infrastructure_circle_dataset,
        name='object_infrastructureCircle_dataset'),

    re_path(r'object_intersections_dataset/(?P<objectResearch_id>\d+)$', objects_intersections_dataset,
        name='object_intersections_dataset'),

]