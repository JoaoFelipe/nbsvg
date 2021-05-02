from lxml.builder import E
from lxml import etree

from .base import StylizedElement
from .text import Text


class TextBox(StylizedElement):
    
    def __init__(self, text, width=None, height=None, fill="white", stroke="blue", align='start', padding=5, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.width = width
        self.height = height
        self.fill = fill
        self.stroke = stroke
        self.padding = padding
        self.align = align

    def build(self, style):
        align = self.align
        text = Text(self.text, textanchor=align).do_build(style)
        self.width = self.width or text.width + 2*self.padding
        self.height = self.height or text.height + 2*self.padding
        if align == 'start':
            text = text.translate(self.padding, self.padding)
        elif align == 'middle':
            text = text.translate(self.width/2, self.padding)
        elif align == 'end':
            text = text.translate(self.width - self.padding, self.padding)
        text = text.do_build(style)
        
        self.element = E.g(
            E.rect({
                'x': '0', 'y': '0', 'width': f'{self.width - 1}', 'height': f'{self.height}',
                'fill': self.fill, 'stroke': self.stroke
            }),
            text.element
        )

class SVGNode(StylizedElement):
    
    def __init__(self, text, width=1, height=1, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.width = width
        self.height = height
        
    def build(self, style):
        self.element = etree.XML(self.text)
