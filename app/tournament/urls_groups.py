from django.urls import path

from tournament import views

urlpatterns = [
    path('', views.groups, name='groups'),
]