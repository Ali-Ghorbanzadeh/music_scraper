import requests
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image as Img
from concurrent.futures import ThreadPoolExecutor
from .models import Artist, Music, Image
from requests.exceptions import SSLError, ConnectTimeout, ConnectionError, ReadTimeout
from django.core.cache import cache


def download_image(url, save_path):
    response = requests.get(url, timeout=3)
    if response.status_code == 200:
        image = Img.open(BytesIO(response.content))
        image.save(f'storage/media/{save_path}')
        print(f"Image downloaded and saved to {save_path}")
        return save_path
    else:
        print(f"Failed to download image. Status code: {response.status_code}")


class Scraper:
    obj = None
    musics = []
    images = []

    def __new__(cls, *args, **kwargs):
        if not cls.obj:
            cls.obj = super().__new__(cls)
        return cls.obj

    @classmethod
    def set_details(cls, music):
        music_url = music.get('href')
        if cache.get(music_url):
            return False

        try:
            music_name = music.find('span').text
            cache.set(key=music_url, value=music_name)
            if not Music.objects.archive().filter(url=music_url).exists():
                music_content = requests.get(music_url, timeout=3).content
                soup = BeautifulSoup(music_content, 'html.parser')
                artist_name = soup.select('.thisinfo')[0].find('a').text

                url = soup.select('.thisinfo')[0].find('a').get('href')
                artist, _ = Artist.objects.archive().get_or_create(name=artist_name, url=url)
                realsed_time = soup.select('.feater > b')[0].text
                q320 = soup.select('.dlbter')[0].get('href') if soup.select('.dlbter') else None
                q120 = soup.select('.dlbter')[1].get('href') if soup.select('.dlbter') else None
                new_music = Music(name=music_name, artist=artist, url=music_url, realsed_time=realsed_time,
                                  download_320=q320, download_120=q120)
                img = 'https://www.ganja2music.com' + soup.select('.insidercover')[0].find('a').get('href')
                alt = soup.select('.insidercover')[0].find('img').get('alt')
                image = Image(music=new_music, src=download_image(img, f'{alt}.jpg'), alt=alt)
                cls.musics.append(new_music)
                cls.images.append(image)
                return True
            return False
        except (SSLError, ConnectTimeout, ConnectionError, ReadTimeout) as e:
            return cls.set_details(music)

    @classmethod
    def fetch(cls, url):
        try:
            content = requests.get(url, timeout=3).content
            musics = BeautifulSoup(content, 'html.parser').select('.dirch > div > a')
            with ThreadPoolExecutor(max_workers=6) as executor:
                executor.map(cls.set_details, musics)

        except (SSLError, ConnectTimeout, ConnectionError, ReadTimeout) as e:
            return cls.fetch(url)

    @classmethod
    def get_all_musics(cls):
        cls.musics, cls.images = [], []
        urls = [f'https://www.ganja2music.com/archive/single/page/{num}/' for num in range(50, 0, -1)]
        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(cls.fetch, urls)
        Music.objects.bulk_create(cls.musics)
        Image.objects.bulk_create(cls.images)

    @classmethod
    def update_musics(cls):
        cls.musics, cls.images = [], []
        for num in range(1, 51):
            content = requests.get(f'https://www.ganja2music.com/archive/single/page/{num}/').content
            musics = BeautifulSoup(content, 'html.parser').select('.dirch > div > a')
            with ThreadPoolExecutor(max_workers=3) as executor:
                details = executor.map(cls.set_details, musics)
            Music.objects.bulk_create(cls.musics)
            Image.objects.bulk_create(cls.images)
            if not all(details):
                break
