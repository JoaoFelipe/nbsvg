from lxml import etree
from lxml.builder import E
from .base import StylizedElement
from .group import Group

class SVGElement(Group):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.etype = lambda: E.svg({'xmlns': 'http://www.w3.org/2000/svg'})

    def build(self, style):
        super().build(style)
        self.element.set('width', f'{self.width}')
        self.element.set('height', f'{self.height}')

    @property
    def xml(self):
        if not self._built:
            self.do_build()
        return etree.tostring(
            self.element, xml_declaration=True, encoding="UTF-8", method="html",
            doctype='<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">'
        )

    def __repr__(self):
        return f'SVGElement(items={self.items})'
