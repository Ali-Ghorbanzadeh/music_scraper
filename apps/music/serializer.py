from rest_framework.serializers import ModelSerializer
from .models import Artist, Music, Image


class ArtistSerializer(ModelSerializer):

    class Meta:
        model = Artist
        fields = ['id',
                  'name',
                  'url',
                  'is_popular',
                  'is_deleted',
                  'all_musics']


class ImageSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class MusicSerializer(ModelSerializer):
    artist = ArtistSerializer()
    image = ImageSerializer()

    class Meta:
        model = Music
        fields = '__all__'
        extra_kwargs = {
            'download_320': {'required': False},
            'download_120': {'required': False},
        }

