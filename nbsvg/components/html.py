from .image import Image
from .base import StylizedElement

class HTML(StylizedElement):

    def __init__(self, html, **kwargs):
        super().__init__(**kwargs)
        self.html = html

    def build(self, style):
        import imgkit
        res = imgkit.from_string(self.html, False)
        image = Image(res).do_build(style)
        self.width = image.width
        self.height = image.height
        self.element = image.element
    
    def __repr__(self):
        return f'HTML({self.html!r})'
