
import base64
from io import BytesIO
from lxml.builder import E
from lxml import etree

from .base import StylizedElement


class Image(StylizedElement):
    
    def __init__(self, url, force_width=None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.force_width = force_width

    def build(self, style):
        from PIL import Image
        fontsize = style.fontsize
        url = self.url
        if isinstance(url, str) and url.startswith('data:'):
            url = base64.b64decode(url.rsplit(',')[-1])
        elif isinstance(url, str) and len(url) > 200:
            url = base64.b64decode(url)
        if isinstance(url, bytes):
            url = BytesIO(url)

        image = Image.open(url)
        width, height = image.size
        self.width = self.force_width or min(width, style.width)
        self.height = height * self.width / width

        #image = image.resize((int(self.width), int(self.height)), Image.ANTIALIAS)

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        self.element = E.image({
            'width': f'{self.width}', 'height': f'{self.height}',
            '{http://www.w3.org/1999/xlink}href': f'data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode("utf-8")}'
        })

    def __repr__(self):
        return f'Image({self.url!r})'


class SVGGroup(StylizedElement):
    
    def __init__(self, svg, default_height=100, **kwargs):
        super().__init__(**kwargs)
        self.svg = svg
        self.default_height = default_height
        
    def build(self, style):
        self.element = etree.XML(self.svg)
        self.width = style.width
        self.height = self.default_height
        if 'width' in self.element.attrib:
            self.width = min(self.width, int(self.element.attrib['width']))
        if 'height' in self.element.attrib:
            self.height = max(self.height, int(self.element.attrib['height']))
        self.element.tag = 'g'
        
    def __repr__(self):
        return f'SVGGroup({self.svg!r})'
