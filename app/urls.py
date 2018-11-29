from django.conf.urls import url
from . import views

# app_name = 'app'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^guardar_simulacion/$', views.guardar_simulacion,
        name='guardar_simulacion'),
    url(r'^simulacion/(?P<id>\d+)/$', views.simulacion, name="simulacion"),
    url(r'^simulaciones/$', views.simulaciones, name='simulaciones'),
]
