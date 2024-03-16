from django.urls import path
from . import views

urlpatterns = [
    path('api/programs/', views.ProgramList.as_view(), name='program-list'),
    path('api/test/', views.test, name='test'),
    path("",views.index, name='index')
]
