from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('send_message/', views.send_message, name='send_message'),
    path('llm_message/', views.llm_message, name='llm_message'),
    path("stats/", views.stats, name="stats"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_chat_view/', views.delete_chat_view, name='delete_chat_view'),
    path('building/', views.world_building, name='building'),
]