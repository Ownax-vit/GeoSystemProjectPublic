import csv
import json

import xlwt
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import F, Max
from django.contrib.gis.geos import Point
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize

from .models import *
from .forms import *



@login_required()
def indexList(request):
    """ Главная страница, со списком исследований """
    list_objectResearch = ObjectResearch.objects.all().order_by('-date_create')

    template = 'index.html'
    paginator = Paginator(list_objectResearch, 9)  # встроенный класс пагинатора
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'list_objectsResearch': list_objectResearch,
        'page_obj': page_obj,
    }
    return render(request, template, context)



@login_required()
def createObjectResearch(request):
    """ Создание исследования """
    template = 'editObjectResearch.html'
    btn_title = 'Создать'
    title = 'Создание'
    form = ObjectResearchForm

    if request.method == "POST":
        objectResearch = ObjectResearch()
        form = ObjectResearchForm(request.POST)
        if form.is_valid():
            objectResearch.name = form.cleaned_data['name']
            objectResearch.description = form.cleaned_data['description']
            objectResearch.author = request.user
            objectResearch.date_create = timezone.now()
            objectResearch.save()
            messages.success(request, 'Исследование создано!')
            return redirect(reverse('index-page'))


    return render(request, template, {
                                       'form': form,
                                       'btn_title': btn_title,
                                        'title': title})


@login_required()
def editObjectResearch(request, objectResearch_id):
    """ Редактирование данных исследования """
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    template = 'editObjectResearch.html'
    btn_title = 'Изменить'
    title = 'Редактирование'
    edit_mode = True
    form = ObjectResearchForm({
        'id': objectResearch.id,
        'name': objectResearch.name,
        'description': objectResearch.description,
        'author': objectResearch.author,
        'date_create': objectResearch.date_create,

    })

    if request.method == 'POST':
        form = ObjectResearchForm(request.POST)
        if form.is_valid():
            objectResearch.name = form.cleaned_data['name']
            objectResearch.description = form.cleaned_data['description']
            objectResearch.save()
            messages.success(request, 'Данные исследования изменены!')
            return redirect(reverse('index-page'))

    return render(request, template, {'form': form,
                                      'id_objectResearch': objectResearch_id,
                                      'edit_mode': edit_mode,
                                      'btn_title': btn_title,
                                      'title': title})


@login_required()
def deleteObjectResearch(request, objectResearch_id):
    """ Удаление исследования """
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    objectResearch.delete()

    # удаляем инфраструктуры без исследований
    for i in ObjectInfrastructure.objects.all():
        if not (i.obj_research.all()):
            i.delete()

    messages.success(request, 'Исследование удалено!')
    return redirect(reverse('index-page'))


@login_required()
def working_ObjectResearch(request, objectResearch_id):
    """ Страница работы с картой"""
    template = 'workingObjectResearch.html'
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    objectsBusiness = ObjectBusiness.objects.filter(obj_research=objectResearch_id).order_by('-date')[:5]
    objectsInfrastructure = ObjectInfrastructure.objects.filter \
        (obj_research__id=objectResearch_id).order_by('-date')[:5]

    # получение объектов пересечения текущего исследования
    objectsIntersections = ObjectIntersections.objects.filter(
        obj_business__obj_research__id=objectResearch_id
    ).order_by('-area')[:5]

    # сложный запрос, суть которого - получение записей объектов бизнеса с максимальной площадью пересечения
    # функция F позволяет отсортировать данные с нулывыми значениями на конец в отличие от обычного '-max_area'
    objectsBusinessRang = ObjectBusiness.objects.filter(obj_research=objectResearch_id). \
        annotate(max_area=Max('objectintersections__area')).order_by(F('max_area').desc(nulls_last=True))[:10]
    return render(request, template, {
        'objectResearch': objectResearch,
        'objectResearch_id': objectResearch.id,
        'objectsBusiness': objectsBusiness,
        'objectsInfrastructure': objectsInfrastructure,
        'objectsIntersections': objectsIntersections,
        'objectsBusinessRang': objectsBusinessRang,
    })


@login_required()
def editObjectBusiness(request, objectResearch_id, objectBusiness_id=None):
    """ Функция добавления и изменения объектов бизнеса"""
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    template = 'editObjectBusiness.html'
    edit_mode = False

    # Если ид объекта бизнеса не приходит, то это создание
    if objectBusiness_id == None:
        objectBusiness = ObjectBusiness(obj_research=objectResearch)
        form = ObjectBussinessForm
        title = 'Создание'
        titleBtn = 'Создать'
        titleEvent = 'создан'
    # если приходит - редактирование
    else:
        objectBusiness = get_object_or_404(ObjectBusiness, id=objectBusiness_id)
        objectBusiness_id  = objectBusiness.id
        title = 'Редактирование'
        titleBtn = 'Редактировать'
        titleEvent = 'изменен'
        edit_mode = True
        long, lat = objectBusiness.geom.coords

        form = ObjectBussinessForm({
            'id': objectBusiness.id,
            'author': objectBusiness.author,
            'date': objectBusiness.date,
            'name': objectBusiness.name,
            'address': objectBusiness.address,
            'source': objectBusiness.source,
            'rent_price': objectBusiness.rent_price,
            'area': objectBusiness.area,
            'pop': objectBusiness.pop,
            'dist_of_ind': objectBusiness.dist_of_ind,
            'geom': objectBusiness.geom,
            'radius': round(objectBusiness.radius, 2),
            'circle': objectBusiness.circle,
            'long': round(long, 5),
            'lat': round(lat, 5)})

    if request.method == 'POST':
        form = ObjectBussinessForm(request.POST)
        if form.is_valid():
            objectBusiness.name = form.cleaned_data['name']
            objectBusiness.address = form.cleaned_data['address']
            objectBusiness.source = form.cleaned_data['source']
            objectBusiness.rent_price = form.cleaned_data['rent_price']
            objectBusiness.area = form.cleaned_data['area']
            objectBusiness.pop = form.cleaned_data['pop']
            objectBusiness.dist_of_ind = form.cleaned_data['dist_of_ind']
            objectBusiness.author = request.user
            objectBusiness.date = timezone.now()
            long = form.cleaned_data['long']
            lat = form.cleaned_data['lat']
            point = form.cleaned_data['geom']

            if not (point):
                if not (long and lat):
                    messages.error(request, 'Некорректно заполнены поля местоположения!')
                    return render(request, template,
                                  {'form': form,
                                   'title': title,
                                   'edit_mode': edit_mode,
                                   'titleButton': titleBtn,
                                   'objectResearch_id': objectResearch_id,
                                   'objectBusiness_id': objectBusiness_id,
                                   })

            if long and lat:
                long = form.cleaned_data['long']
                lat = form.cleaned_data['lat']
                point = Point(long, lat)

            objectBusiness.geom = point
            objectBusiness.save()
            messages.success(request, 'Объект бизнеса {} {}!'.format(objectBusiness.id, titleEvent))

            # если редактирование, то переадресация на страницу объектов бизнеса
            if edit_mode:
                return HttpResponseRedirect(reverse('all_ObjectsBusiness-page', args=[objectResearch_id]))

            return HttpResponseRedirect(reverse('working_ObjectResearch-page', args=[objectResearch_id]))

    return render(request, template,
                      {'form': form,
                       'title': title,
                       'edit_mode': edit_mode,
                       'titleButton': titleBtn,
                       'objectResearch_id': objectResearch_id,
                       'objectBusiness_id': objectBusiness_id,
                       })


@login_required()
def deleteObjectBusiness(request, objectBusiness_id):
    """ Удаление объектов бизнеса """
    objectBusiness = get_object_or_404(ObjectBusiness, id=objectBusiness_id)
    objectResearch_id = objectBusiness.obj_research.id
    objectBusiness.delete()

    messages.success(request, 'Объект бизнеса удален!')
    return HttpResponseRedirect(reverse('all_ObjectsBusiness-page', args=[objectResearch_id]))


@login_required()
def allObjectsBusiness(request, objectResearch_id):
    """ Страница всех объектов бизнеса """
    template = 'objectsBusiness.html'
    objectsBusiness = ObjectBusiness.objects.filter(obj_research=objectResearch_id).order_by('-date')
    paginator = Paginator(objectsBusiness, 20) # встроенный класс пагинатора
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {'page_obj': page_obj,
                                      'objectResearch_id': objectResearch_id,
                                      })



#  Работа с объектами инфраструктуры
# Создание объекта инфраструктуры
@login_required()
def createObjectInfrastructure(request, objectResearch_id):
    """ Работа с объектами инфраструктуры Создание объекта инфраструктуры """
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    template = 'editObjectInfrastructure.html'
    form = ObjectInfrastructureForm
    title = 'Создание'
    titleBtn = 'Создать'

    if request.method == "POST":
        form = ObjectInfrastructureForm(request.POST)
        if form.is_valid():
            objectInfrastructure = ObjectInfrastructure()

            objectInfrastructure.name = form.cleaned_data['name']
            objectInfrastructure.address = form.cleaned_data['address']
            objectInfrastructure.radius = form.cleaned_data['radius']
            objectInfrastructure.author = request.user
            objectInfrastructure.date = timezone.now()
            long = form.cleaned_data['long']
            lat = form.cleaned_data['lat']
            point = form.cleaned_data['geom']

            if not (point):
                if not (long and lat):
                    messages.error(request, "Данные местоположения неверны!")
                    return render(request, template, {'form': form,
                                                      'objectResearch_id': objectResearch_id,
                                                      'title': title,
                                                      'titleButton': titleBtn,
                                                      })
            if long and lat:
                long = form.cleaned_data['long']
                lat = form.cleaned_data['lat']
                point = Point(long, lat)


            objectInfrastructure.geom = point
            objectInfrastructure.save()

            # добавляем привязку к объекту исследования
            objectInfrastructure.obj_research.add(objectResearch)
            objectInfrastructure.save()

            messages.success(request, 'Объект инфраструктуры создан')
            return HttpResponseRedirect(reverse('working_ObjectResearch-page',
                                                args=[objectResearch_id]))

    return render(request, template, {'form': form,
                                      'objectResearch_id': objectResearch_id,
                                      'title': title,
                                      'titleButton': titleBtn,
                                      })


@login_required()
def editObjectInfrastructure(request, objectResearch_id, objectInfrastructure_id):
    """ Редактирование объекта инфраструктуры """
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    objectInfrastructure = get_object_or_404(ObjectInfrastructure, id=objectInfrastructure_id)
    template = 'editObjectInfrastructure.html'
    edit_mode = True
    title = 'Редактирование'
    titleBtn = 'Редактировать'

    long, lat = objectInfrastructure.geom.coords
    form = ObjectInfrastructureForm({
            'id': objectInfrastructure.id,
            'author': objectInfrastructure.author,
            'date': objectInfrastructure.date,
            'name': objectInfrastructure.name,
            'address': objectInfrastructure.address,
            'radius': round(objectInfrastructure.radius,2),
            'geom': objectInfrastructure.geom,
            'circle': objectInfrastructure.circle,
            'long': round(long, 5),
            'lat': round(lat, 5),
        })

    if request.method == "POST":
        form = ObjectInfrastructureForm(request.POST)
        if form.is_valid():
            objectInfrastructure.name = form.cleaned_data['name']
            objectInfrastructure.address = form.cleaned_data['address']
            objectInfrastructure.radius = form.cleaned_data['radius']
            objectInfrastructure.author = request.user
            objectInfrastructure.date = timezone.now()
            long = form.cleaned_data['long']
            lat = form.cleaned_data['lat']

            point = form.cleaned_data['geom']
            if not (point):
                if not (long and lat):
                    messages.error(request, "Данные местоположения неверны!")
                    return render(request, template, {'form': form})
            if long and lat:
                long = form.cleaned_data['long']
                lat = form.cleaned_data['lat']
                point = Point(long, lat)


            objectInfrastructure.geom = point
            objectInfrastructure.save()

            messages.success(request, 'Объект инфраструктуры изменен!')
            return HttpResponseRedirect(reverse('all_ObjectsInfrastructure-page',
                                                args=[objectResearch_id]))
    return render(request, template,
                  {'form': form,
                   'title': title,
                   'edit_mode': edit_mode,
                   'titleButton': titleBtn,
                   'objectResearch_id': objectResearch_id,
                   'objectInfrastructure_id': objectInfrastructure_id,
                   })

@login_required()
def deleteObjectInfrastructure(request, objectResearch_id, objectInfrastructure_id):
    """ Удаление объекта инфраструктуры """
    objectInfrastructure = get_object_or_404(ObjectInfrastructure, id=objectInfrastructure_id)
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    objectResearch.objectinfrastructure_set.remove(objectInfrastructure)

    # если связанных объектов не осталось - удалить инфраструктуру
    if not(objectInfrastructure.obj_research.all()):
        objectInfrastructure.delete()

    messages.success(request, 'Объект инфраструктуры удален!')
    return HttpResponseRedirect(reverse('all_ObjectsInfrastructure-page',
                                        args=[objectResearch_id]))


@login_required()
def allObjectInfrastructure(request, objectResearch_id):
    """ Страница всех объектов инфраструктуры """
    template = 'objectsInfrastructure.html'
    objectsInfrastructure = ObjectInfrastructure.objects.filter(
        obj_research=objectResearch_id).order_by('-date')
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    paginator = Paginator(objectsInfrastructure, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = ImportInfrastructureForm()

    if request.method == 'POST':
        # импорт инфраструктуры из другого исследования
        form = ImportInfrastructureForm(request.POST)
        if form.is_valid():
            objResearchFromImport = form.cleaned_data['id_researchFromImport']
            objectsInfrastructureFrom = ObjectInfrastructure.objects.filter(
                obj_research=objResearchFromImport.id)
            for obj in objectsInfrastructureFrom:
                obj.obj_research.add(objectResearch)

            if objectsInfrastructureFrom:
                messages.success(request, 'Объекты инфраструктуры импортированы!')
            else:
                messages.error(request,
                               'Объекты инфраструктуры для импорта в выбранном исследовании не найдены!')

            return HttpResponseRedirect(reverse('all_ObjectsInfrastructure-page',
                                                args=[objectResearch_id]))

    return render(request, template, {'page_obj': page_obj,
                                      'objectResearch_id': objectResearch_id,
                                      'form': form,
                                      })


@login_required()
def calc_objectIntersections(request, objectResearch_id):
    """  Нахождение объектов пересечения """
    objectResearch = get_object_or_404(ObjectResearch, id=objectResearch_id)
    objectsBusiness = ObjectBusiness.objects.filter(obj_research=objectResearch_id)
    objectsInfrastructure = ObjectInfrastructure.objects.filter(obj_research=objectResearch_id)

    # удаляем объекты пересечения если они есть для текущего исследования
    if ObjectIntersections.objects.filter(
        obj_business__obj_research__id=objectResearch_id
    ):
        ObjectIntersections.objects.filter(
            obj_business__obj_research__id=objectResearch_id
        ).delete()

    # записываем окружности и идентификаторы объектов в словари
    dictBusiness = { x.id: x.circle.transform(32637, clone=True) for x in objectsBusiness }
    dictInfr = { x.id: x.circle.transform(32637, clone=True) for x in objectsInfrastructure }

    # обходим все объекты инфр по всем объектам бизнеса в поисках пересечения
    for keyInfr, circleInfr in dictInfr.items():
        circleInfr = circleInfr
        for keyBus, circleBus in dictBusiness.items():
            # если окружность инфраструктуры пересекает окруж. бизнеса
            # создаем новый объект пересечения
            # .intersects возвращает True если пересекает
            if circleInfr.intersects(circleBus):
                geomIntersections = circleInfr.intersection(circleBus)
                areaIntersections = round(geomIntersections.area, 4)
                objectBus = ObjectBusiness.objects.get(id=keyBus)
                objectInfr = ObjectInfrastructure.objects.get(id=keyInfr)
                objectIntersections = ObjectIntersections(obj_business=objectBus,
                                                          obj_infrastructure=objectInfr,
                                                          )
                objectIntersections.geom = geomIntersections
                objectIntersections.area = areaIntersections
                objectIntersections.save()

    messages.success(request, 'Объекты пересечения обновлены')
    return redirect(reverse('working_ObjectResearch-page', args=[objectResearch_id]))

@login_required()
def view_objectIntersections(request, objectIntersections_id):
    """ Страница изучения объекта пересечения"""
    objectIntersection = get_object_or_404(ObjectIntersections, id=objectIntersections_id)
    template = 'viewObjectIntersections.html'
    objectResearch_id = objectIntersection.obj_business.obj_research.id

    form = FormViewIntersectionObject({
        'obj_business': objectIntersection.obj_business.id,
        'obj_infrastructure': objectIntersection.obj_infrastructure.id,
        'geom': objectIntersection.geom,
        'area': round(objectIntersection.area, 2)
    })

    return render(request, template, {'form': form,
                                      'objectIntersection': objectIntersection,
                                      'objectResearch_id': objectResearch_id})


@login_required()
def allObjectIntersections(request, objectResearch_id):
    """ Страница всех объектов пересечения """
    template = 'objectsIntersections.html'
    objectsIntesections = ObjectIntersections.objects.filter(
        obj_business__obj_research__id=objectResearch_id
    )
    paginator = Paginator(objectsIntesections, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {'page_obj': page_obj,
                                      'objectResearch_id': objectResearch_id})


@login_required()
def allObjectBusinessRanging(request, objectResearch_id):
    """ Страница со всеми ранжированными объектами бизнеса"""
    objectsBusinessRang = ObjectBusiness.objects.filter(obj_research=objectResearch_id).\
        annotate(max_area=Max('objectintersections__area')).order_by(F('max_area').desc(nulls_last=True))
    avgRent = objectsBusinessRang.aggregate(avg=Avg('rent_price'))
    data = []
    for i in objectsBusinessRang:
        if i.max_area != None:
            data.append(i.max_area)
        else:
            data.append(0)

    template = 'objectsBusinessRanging.html'
    paginator = Paginator(objectsBusinessRang, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, template, {
                                      'objectResearch_id': objectResearch_id,
                                      'avgRent': avgRent,
                                      'page_obj': page_obj,
                                       'data':data,
                                      'all_objects_business': objectsBusinessRang,

                    })


@login_required()
def export_business_xls(request, objectResearch_id):
    """ экспорт объектов бизнеса в xlx """
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="objectBusiness.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['id', 'name', 'address', 'source', 'rent_price', 'area', 'pop',
               'dist_of_ind', 'radius', 'lat', 'long' ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = [(obj.id, obj.name, obj.address, obj.source, obj.rent_price, obj.area, obj.pop, obj.dist_of_ind,
                        obj.radius, obj.geom.coords[1], obj.geom.coords[0]) for obj in
                       ObjectBusiness.objects.filter(obj_research=objectResearch_id).
                           annotate(max_area=Max('objectintersections__area')).order_by(
                           F('max_area').desc(nulls_last=True))]
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@login_required()
def export_business_csv(request, objectResearch_id):
    """ экспорт объектов бизнеса в csv """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="business.csv"'
    response.write(u'\ufeff'.encode('utf8')) # как это работает и что за чудеса?

    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'address', 'source', 'rent_price', 'area', 'pop',
               'dist_of_ind', 'radius', 'lat', 'long'])

    objectsBusiness = [(obj.id, obj.name, obj.address, obj.source, obj.rent_price, obj.area, obj.pop, obj.dist_of_ind,
                            obj.radius,  obj.geom.coords[1], obj.geom.coords[0]) for obj in
                           ObjectBusiness.objects.filter(obj_research=objectResearch_id).
                               annotate(max_area=Max('objectintersections__area')).order_by(
                               F('max_area').desc(nulls_last=True))]
    for object in objectsBusiness:
        writer.writerow(object)

    return response


@login_required()
def export_infrastructure_xls(request, objectResearch_id):
    """ экспорт объектов инфраструктуры в xlx """
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="objectsInfrastructure.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['id', 'name', 'address',  'radius', 'lat', 'long']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    objectsInfratructure= [(obj.id, obj.name, obj.address, obj.radius, obj.geom.coords[1], obj.geom.coords[0]) for obj
                           in ObjectInfrastructure.objects.filter(obj_research=objectResearch_id).
                           annotate(max_area=Max('objectintersections__area')).order_by(
                           F('max_area').desc(nulls_last=True))]
    for row in objectsInfratructure:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@login_required()
def export_infrastructure_csv(request, objectResearch_id):
    """ экспорт объектов инфраструктуры в csv """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="objectsInfrastructure.csv"'
    response.write(u'\ufeff'.encode('utf8')) # как это работает и что за чудеса?

    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'address',  'radius', 'lat', 'long'])

    objectsInfratructure = [(obj.id, obj.name, obj.address, obj.radius, obj.geom.coords[1], obj.geom.coords[0]) for obj
                            in
                            ObjectInfrastructure.objects.filter(obj_research=objectResearch_id).
                                annotate(max_area=Max('objectintersections__area')).order_by(
                                F('max_area').desc(nulls_last=True))]
    for object in objectsInfratructure:
        writer.writerow(object)

    return response


@login_required()
def export_objectsBusinessRang_xls(request, objectResearch_id):
    """ экспорт ранжированных объектов бизнеса в xlx """
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="objectBusinessRang.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['id', 'name', 'address', 'source', 'rent_price', 'area', 'pop',
               'dist_of_ind', 'radius', 'max_area', 'lat', 'long']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    objectsBusinessRang = [(obj.id, obj.name, obj.address, obj.source, obj.rent_price, obj.area, obj.pop, obj.dist_of_ind,
                            obj.radius, obj.max_area, obj.geom.coords[1], obj.geom.coords[0]) for obj in
                           ObjectBusiness.objects.filter(obj_research=objectResearch_id).
                               annotate(max_area=Max('objectintersections__area')).order_by(
                               F('max_area').desc(nulls_last=True))]

    for row in objectsBusinessRang:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@login_required()
def export_objectsBusinessRang_csv(request, objectResearch_id):
    """ экспорт ранжированных объектов бизнеса в csv """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="businessRang.csv"'
    response.write(u'\ufeff'.encode('utf8')) # как это работает и что за чудеса?

    writer = csv.writer(response)
    writer.writerow(['id', 'name', 'address', 'source', 'rent_price', 'area', 'pop',
               'dist_of_ind', 'radius', 'max_area', 'lat', 'long'])

    objectsBusinessRang = [(obj.id, obj.name, obj.address, obj.source, obj.rent_price, obj.area, obj.pop, obj.dist_of_ind,
                            obj.radius, obj.max_area, obj.geom.coords[1], obj.geom.coords[0]) for obj
                           in ObjectBusiness.objects.filter(obj_research=objectResearch_id).
                           annotate(max_area=Max('objectintersections__area')).order_by(F('max_area'
                                                                                          ).desc(nulls_last=True))]

    for object in objectsBusinessRang:
        writer.writerow(object)

    return response

@login_required()
def objects_business_dataset(request, objectResearch_id):
    """ Преобразуем в geojson, геометрическое поле для отображения - geom """
    markers_business = serialize('geojson', ObjectBusiness.objects.filter(obj_research=objectResearch_id),
                                             geometry_field='geom')
    return HttpResponse(markers_business, content_type='json')

@login_required()
def objects_infrastructure_dataset(request, objectResearch_id):
    markers_infrastructure = serialize('geojson', ObjectInfrastructure.objects.filter \
        (obj_research__id=objectResearch_id), geometry_field='geom')
    return HttpResponse(markers_infrastructure, content_type='json')

@login_required()
def objects_business_circle_dataset(request, objectResearch_id):
    obj_business = ObjectBusiness.objects.filter(obj_research=objectResearch_id)
    output_dict = []
    # создаем словарь для формирования списка окружностей бизнеса вручную
    # так как поле окружности не существует в БД
    # в формате geojson (json)
    results = list(obj_business)
    for res in results:
        rec = {}
        rec['type'] = "Feature"
        # преобразование в подходящие координаты для вычисления окружностей
        pointBus = res.geom.transform(32637, clone=True)
        circleBus = pointBus.buffer(res.radius)
        # обратное преобразование координат
        circleBus.transform(4326)
        rec['geometry'] = json.loads(circleBus.geojson)
        rec['properties'] = {"pk": res.id, "radius": res.radius}
        output_dict.append(rec)
    circle_business = json.dumps(output_dict)
    # circle_business = serialize('geojson', ObjectBusiness.objects.filter(obj_research=objectResearch_id),
    #                                         geometry_field='circle')
    return HttpResponse(circle_business, content_type='json')

@login_required()
def objects_infrastructure_circle_dataset(request, objectResearch_id):
    obj_infrastructure = ObjectInfrastructure.objects.filter(obj_research__id=objectResearch_id)
    output_dict = []

    results = list(obj_infrastructure)
    for res in results:
        rec = {}
        rec['type'] = "Feature"
        # преобразование в подходящие координаты для вычисления окружностей
        pointInfr = res.geom.transform(32637, clone=True)
        circleInfr = pointInfr.buffer(res.radius)
        # обратное преобразование координат
        circleInfr.transform(4326)
        rec['geometry'] = json.loads(circleInfr.geojson)
        rec['properties'] = {"pk": res.id, "radius": res.radius}
        output_dict.append(rec)
    circle_infrastructure = json.dumps(output_dict)

    # circle_infrastructure = serialize('geojson', ObjectInfrastructure.objects.filter \
    #     (obj_research__id=objectResearch_id), geometry_field='circle')
    return HttpResponse(circle_infrastructure, content_type='json')

@login_required()
def objects_intersections_dataset(request, objectResearch_id):
    circle_intersections = serialize('geojson', ObjectIntersections.objects.filter(
        obj_business__obj_research__id=objectResearch_id), geometry_field='geom')

    return HttpResponse(circle_intersections, content_type='json')

