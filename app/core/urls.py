from django.urls import path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("info/", views.info, name="info"),
    path("match/<int:match_number>/", views.match_detail, name="match_detail"),
    path("rankings/", views.rankings, name="rankings"),
    path("painel/", views.admin_dashboard, name="admin_dashboard"),
    path("painel/match/<int:match_number>/edit/", views.admin_match_edit, name="admin_match_edit"),
]