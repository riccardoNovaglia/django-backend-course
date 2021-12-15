from django.urls import path

from cats import views

urlpatterns = [
    path('hello', views.cats),
    path('greet', views.greet)
]
