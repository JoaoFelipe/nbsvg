from lxml.builder import E

from .base import StylizedElement
from .group import Group
from .text import Line, TSpan

class List(StylizedElement):
            
    def __init__(self, group, ordered, **kwargs):
        super().__init__(**kwargs)
        self.group = group
        self.ordered = ordered
        
    def build(self, style):
        group = self.group.translate(25, 0).do_build(style, width=style.width - 25)
        side_group = Group()
        for i, item in enumerate(group):
            text = "•"
            if self.ordered:
                text = f'{i + 1}.'
            side_group.add(Line([TSpan(text)]).translate(0, item.y))
            
        side = 15
        if self.ordered:
            side = 10
        side_group = side_group.translate(side, 0).do_build(style)
        self.element = E.g(side_group.element, group.element)
        self.width = group.width + 25
        self.height = group.height
        
    def __repr__(self):
        return f'List({self.group!r}, {self.ordered!r})'
