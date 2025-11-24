import sys
import os
import django
from django.test import Client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'miespacio.settings')
django.setup()
from django.conf import settings as _settings
# ensure test client host allowed when running standalone
if not _settings.ALLOWED_HOSTS:
    _settings.ALLOWED_HOSTS = ['testserver', '127.0.0.1', 'localhost']
client = Client()
r = client.get('/')
print('status', r.status_code)
s = r.content.decode('utf-8')
# find image srcs
from html.parser import HTMLParser
class ImgParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.imgs = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'img':
            attrs = dict(attrs)
            if 'src' in attrs:
                self.imgs.append(attrs['src'])

p = ImgParser()
p.feed(s)
print('found images:', len(p.imgs))
for i in p.imgs[:10]:
    print(i)
