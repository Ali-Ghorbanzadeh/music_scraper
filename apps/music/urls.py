from rest_framework.routers import DefaultRouter
from .views import MusicViewSet, ArtistMusicsViewSet, PopularArtistListAPIView, SearchMusicsAPIView, SearchArtistsAPIView
from django.urls import path

router = DefaultRouter()
router.register('api/musics', MusicViewSet, basename='musics')
router.register('api/artists', ArtistMusicsViewSet, basename='artists')

urlpatterns = [
    path('api/popular-artists/', PopularArtistListAPIView.as_view(), name='popular-artists'),
    path('api/search-musics/<name>/', SearchMusicsAPIView.as_view(), name='search-musics'),
    path('api/search-artists/<name>/', SearchArtistsAPIView.as_view(), name='search-artists'),
]

urlpatterns += router.urls
