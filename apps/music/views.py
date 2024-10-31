from .models import Music
from rest_framework.viewsets import ModelViewSet
from .scraper import Scraper
from .serializer import MusicSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from time import time
from django.core.cache import cache
from rest_framework.response import Response


@method_decorator(cache_page(30), name='list')
class MusicViewSet(ModelViewSet):
    queryset = Music.objects.all().order_by('-id')
    serializer_class = MusicSerializer
    first_scraped = False

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

    def get_object(self):
        self.queryset = Music.objects.archive()
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        music = cache.get(kwargs.get('pk'))
        if music is None:
            instance = self.get_object()
            cache.set(
                key=kwargs.get('pk'),
                value=instance,
                timeout=60,
            )
            print('cashed')
            return super().retrieve(request, *args, **kwargs)
        serializer = self.get_serializer(music)
        return Response(serializer.data)







