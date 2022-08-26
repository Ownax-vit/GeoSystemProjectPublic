from django.contrib.gis.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg, Max


class ObjectResearch(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_create = models.DateTimeField(auto_now=False)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Автор',
                               blank=True, null=True)

    def __str__(self):
        return str(self.id)


class ObjectBusiness(models.Model):
    name = models.CharField(max_length=255)
    obj_research = models.ForeignKey(ObjectResearch,
                                     on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True)
    source = models.URLField(max_length=255, null=True)
    date = models.DateTimeField(max_length=255)
    rent_price = models.FloatField()
    area = models.FloatField()
    pop = models.FloatField()
    dist_of_ind = models.FloatField()
    geom = models.PointField(srid=4326, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Автор',
                               blank=True, null=True)

    def __str__(self):
        return str(self.id)

    # метод, возвращающий радиус объекта
    @property  # вызывается как атрибут
    def radius(self):
        # формула скрыта
        pass

    # метод, возвращающий окружность объекта
    @property
    def circle(self):
        pointBus = self.geom.transform(32637, clone=True)
        # строим окружность нужного радиуса
        circleBus = pointBus.buffer(self.radius)
        # обратное преобразование координат
        circleBus.transform(4326)
        return circleBus


class ObjectInfrastructure(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    obj_research = models.ManyToManyField(ObjectResearch)
    date = models.DateTimeField()
    radius = models.FloatField(blank=True, null=True)
    geom = models.PointField(srid=4326, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Автор',
                               blank=True, null=True)

    def __str__(self):
        return str(self.id)

    # метод, возвращающий окружность объекта
    @property
    def circle(self):
        pointInfr = self.geom.transform(32637, clone=True)
        # строим окружность нужного радиуса
        circleInfr = pointInfr.buffer(self.radius)
        # обратное преобразование координат
        circleInfr.transform(4326)
        return circleInfr


class ObjectIntersections(models.Model):
    obj_business = models.ForeignKey(ObjectBusiness,
                                     on_delete=models.CASCADE)
    obj_infrastructure = models.ForeignKey(ObjectInfrastructure,
                                           on_delete=models.CASCADE)
    geom = models.PolygonField(srid=4326, blank=True)
    area = models.FloatField()


    def __str__(self):
        return str(self.obj_business) + str(self.obj_infrastructure)



