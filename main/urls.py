from django.urls import path
from . import views

urlpatterns = [
    # path('favicon.ico', views.favicon),
    path('', views.home),
    path('anime/<str:anime>/', views.get_anime),
    path('episode/<str:anime>/<int:episode>/', views.get_episode),
    path('search',views.search_anime),
    path('embed',views.get_embed),
    path('api/latest/<int:page>/', views.latest_view, name='latest'),
]