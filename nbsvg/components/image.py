
import base64
from io import BytesIO
from lxml.builder import E

from .base import StylizedElement


class Image(StylizedElement):
    
    def __init__(self, url, **kwargs):
        super().__init__(**kwargs)
        self.url = url

    def build(self, style):
        from PIL import Image
        fontsize = style.fontsize
        url = self.url
        if isinstance(url, str) and url.startswith('data:'):
            url = base64.b64decode(url.rsplit(',')[-1])
        if isinstance(url, bytes):
            url = BytesIO(url)

        image = Image.open(url)
        width, height = image.size
        self.width = min(width, style.width)
        self.height = height * self.width / width
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        self.element = E.image({
            'width': f'{self.width}', 'height': f'{self.height}',
            '{http://www.w3.org/1999/xlink}href': f'data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode("utf-8")}'
        })

    def __repr__(self):
        return f'Image({self.url!r})'
