from lxml.html import document_fromstring
from lxml.builder import E

from .base import StylizedElement
from .table import DataframeTable
from .image import Image, SVGGroup
from .text import Text
from .markdown import Markdown
from .group import GroupSequence


class Error(StylizedElement):
    
    def __init__(self, error, **kwargs):
        super().__init__(**kwargs)
        self.error = error
        
    def build(self, style):
        group = GroupSequence()
        for line in self.error.get('traceback', []):
            group.add(Text(line))
        group = group.do_build(style)
        self.element = E.g(
            E.rect({
                'x': '0', 'y': '0', 'width': f'{style.width}', 'height': f'{group.height}',
                'fill': 'rgb(255, 221, 221)',
            }),
            group.element
        )
        self.width = style.width
        self.height = group.height
        
    def __repr__(self):
        return f'Error({self.error!r})'


def html_output(html, **kwargs):
    dom = document_fromstring(html)
    tables = dom.xpath("//table")
    if tables and tables[0].attrib.get('class') == 'dataframe':
        return DataframeTable(dom, **kwargs)
    import imgkit
    res = imgkit.from_string(html, False)
    return Image(res)


def stream_output(data):
    if data.get('name', '') == 'stderr':
        return Error(data['text'].split('\n'))
    return Text(data['text'].rstrip())


def display_data(data, **kwargs):
    if 'text/html' in data:
        return html_output(data['text/html'], **kwargs)
    if 'text/markdown' in data:
        return Markdown(data['text/markdown'], **kwargs)
    if 'image/svg+xml' in data:
        return SVGGroup(data['image/svg+xml'], **kwargs)
    if 'image/png' in data:
        return Image(data['image/png'], **kwargs)
    if 'image/jpeg' in data:
        return Image(data['image/jpeg'], **kwargs)
    if 'text/plain' in data:
        return Text(data['text/plain'].rstrip(), **kwargs)
    return Text(f'Unsupported mimetypes: {", ".join(data.keys())}')
    
