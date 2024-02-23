from django.urls import path
from . import views

urlpatterns = [
    path('programs/', views.ProgramList.as_view(), name='program-list'),
    path('test/', views.test, name='test'),
]
