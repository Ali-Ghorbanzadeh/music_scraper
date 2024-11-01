from .models import Music, Artist
from rest_framework.viewsets import ModelViewSet
from .scraper import Scraper
from .serializer import MusicSerializer, ArtistSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from time import time
from apps.core.models import CacheRetrieveMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView


@method_decorator(cache_page(60 * 60), name='list')
class MusicViewSet(CacheRetrieveMixin, ModelViewSet):
    queryset = Music.objects.all().order_by('realsed_time')
    serializer_class = MusicSerializer
    first_scraped = False
    cache_time = 10

    def list(self, request, *args, **kwargs):
        if not self.__class__.first_scraped:
            start = time()
            Scraper.get_all_musics()
            print(time() - start)
            self.__class__.first_scraped = True
        else:
            Scraper.update_musics()
            print('updated')
        return super().list(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete()


@method_decorator(cache_page(60 * 60), name='list')
class ArtistMusicsViewSet(CacheRetrieveMixin, ModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    cache_time = 60 * 5


@method_decorator(cache_page(60 * 60), name='list')
class PopularArtistListAPIView(ListAPIView):
    queryset = Artist.objects.filter(is_popular=True)
    serializer_class = ArtistSerializer


@method_decorator(cache_page(60 * 60), name='retrieve')
class SearchMusicsAPIView(CacheRetrieveMixin, RetrieveAPIView):
    queryset = Music.objects.all().order_by('realsed_time')
    serializer_class = MusicSerializer
    lookup_field = 'name'
    cache_time = 60 * 60


@method_decorator(cache_page(60 * 60), name='retrieve')
class SearchArtistsAPIView(CacheRetrieveMixin, RetrieveAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    lookup_field = 'name'
    cache_time = 60 * 60









