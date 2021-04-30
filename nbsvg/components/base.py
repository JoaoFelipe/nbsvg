from lxml import etree
from .. import style as main_style


class StylizedElement:

    def __init__(self, *args, **kwargs):
        self._built = False
        self.x = self.y = 0
        self.kwargs = kwargs

    def do_build(self, style=None, **kwargs):
        if not style:
            style = main_style.STYLE
        style = style.apply({**self.kwargs, **kwargs}, this=False)
        self.build(style)
        if self.x != 0 or self.y != 0:
            self.element.set('transform', f'translate({self.x}, {self.y})')
        self._built = True
        return self

    def translate(self, x, y, add=False):
        if add:
            x, y = self.x + x, self.y + y
        self.x, self.y = x, y
        return self

    @property
    def xml(self):
        if not self._built:
            self.do_build()
        return etree.tostring(self.element)

    def __repr__(self):
        return 'StylizedElement()'
