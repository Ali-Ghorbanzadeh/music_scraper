from rest_framework.routers import DefaultRouter
from .views import MusicViewSet
from django.urls import path

router = DefaultRouter()
router.register('api/musics', MusicViewSet)

urlpatterns = []

urlpatterns += router.urls
