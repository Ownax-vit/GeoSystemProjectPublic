import random
import time

from django.utils import timezone
from django.contrib.gis.geos import Point
from django.test import TestCase

from .models import *

def benchmark(funct):
    def wrapper():
        start = time.time()
        funct()
        end = time.time()
        timedif = end - start
        print('-' * 6)
        print('Время выполнения: {}'.format(timedif))
    return wrapper


@benchmark
def createResearch():
    names = ['наименование объект 1', 'наименование объект 2', 'наименование объект 3', 'наименование объект 4']
    obj_research = ObjectResearch(name='Автоматически созданное исследование для тестирования',
                                  date_create=timezone.now(),
                                  description='Тестирование добавления объектов')
    obj_research.save()
    for i in range(300):
        objectBusiness = ObjectBusiness(obj_research=obj_research)
        objectInfrastructure = ObjectInfrastructure()

        objectBusiness.name = random.choice(names)
        objectBusiness.address = 'sdsd'
        objectBusiness.rent_price = random.randint(20000, 70000
                                                   )
        objectBusiness.area = random.randint(20, 100)
        objectBusiness.pop = random.randint(100, 500)
        objectBusiness.dist_of_ind = random.randint(100, 500)
        objectBusiness.author = None
        objectBusiness.date = timezone.now()
        long, lat = random.random() * (36.65898 - 36.4468) + 36.4468, \
                    random.random() * (50.70151 - 50.57315) + 50.57315
        point = Point(long, lat)
        objectBusiness.geom = point
        objectBusiness.save()

        objectInfrastructure.name = random.choice(names)
        objectInfrastructure.address = 'Test address'
        objectInfrastructure.radius = random.randint(100, 900)
        objectInfrastructure.author = None
        objectInfrastructure.date = timezone.now()

        long, lat = random.random() * (36.65898 - 36.4468) + 36.4468, \
                    random.random() * (50.70151 - 50.57315) + 50.57315
        point = Point(long, lat)
        objectInfrastructure.geom = point
        objectInfrastructure.save()

        objectInfrastructure.obj_research.add(obj_research)
        objectInfrastructure.save()
    calc_objectIntersections(obj_research)




def calc_objectIntersections(objectResearch):
    objectResearch = objectResearch
    objectsBusiness = ObjectBusiness.objects.filter(obj_research=objectResearch.id)
    objectsInfrastructure = ObjectInfrastructure.objects.filter(obj_research=objectResearch.id)

    dictBusiness = {x.id: x.circle.transform(32637, clone=True) for x in objectsBusiness}
    dictInfr = {x.id: x.circle.transform(32637, clone=True) for x in objectsInfrastructure}



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
    print('---calc is ready--')

if __name__ == '__main__':
    createResearch()