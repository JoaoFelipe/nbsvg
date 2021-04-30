from lxml.builder import E

from .base import StylizedElement


class Group(StylizedElement):
    
    def __init__(self, items=None, etype=E.g, **kwargs):
        super().__init__(**kwargs)
        self.items = items or []
        self.etype = etype

    def build(self, style):
        self.element = self.etype()
        self.height = self.width = 0
        for item in self.items:
            self.element.append(item.do_build(style).element)
            self.height = max(self.height, item.y + item.height)
            self.width = max(self.width, item.x + item.width)

    def add(self, obj):
        self.items.append(obj)
        return self

    def __iter__(self):
        return iter(self.items)

    def __repr__(self):
        return f'Group(items={self.items!r})'


class GroupSequence(StylizedElement):
    
    def __init__(self, items=None, etype=E.g, **kwargs):
        super().__init__(**kwargs)
        self.items = items or []
        self.etype = etype

    def build(self, style):
        self.element = self.etype()
        self.height = style.group_margin
        self.width = 0
        for obj, sep in self.items:
            self.element.append(
                obj
                .translate(0, self.height, add=True)
                .do_build(style).element
            )
            self.height += obj.height + sep
            self.width = max(self.width, obj.width)

    def __add__(self, other):
        if isinstance(other, str):
            self.add(Text(f"Unsupported: {other}"))
        else:
            self.add(other)
        return self
        
    def add(self, obj, sep=0):
        self.items.append((obj, sep))
        return self

    def __iter__(self):
        return iter(item for item, _ in self.items)

    def __repr__(self):
        return f'GroupSequence(items={self.items})'


def force_groupsequence(text):
    if isinstance(text, GroupSequence):
        return text
    result = GroupSequence()
    if text:
        result.add(text)
    return result    
