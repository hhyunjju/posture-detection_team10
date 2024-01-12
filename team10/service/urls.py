from django.urls import path
from . import views


app_name = 'service'  # 앱 이름 설정

urlpatterns = [
    path('service/', views.service, name='service'),
    path('statistics/', views.statistics, name='statistics'),
    path('game/', views.game, name='game'), 
    path('send_image/', views.send_image, name='send_image'),
    path('send_image_game/', views.send_image_game, name='send_image_game'),
]