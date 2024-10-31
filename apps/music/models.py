from django.db import models
from apps.core.models import TimeStampMixin, LogicalDeleteMixin


class Artist(TimeStampMixin, LogicalDeleteMixin):
    name = models.CharField(max_length=255, unique=True)
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Music(LogicalDeleteMixin):
    name = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='musics')
    url = models.URLField(unique=True)
    realsed_time = models.CharField(max_length=255)
    download_320 = models.URLField(null=True, blank=True)
    download_120 = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ('name', 'artist')

    def __str__(self):
        return self.name


class Image(TimeStampMixin):
    music = models.OneToOneField(Music, on_delete=models.CASCADE, related_name='image')
    src = models.ImageField(upload_to='media')
    alt = models.TextField()

    def __str__(self):
        return f'{self.music.name}: {self.src.url}'
