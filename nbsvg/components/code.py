from lxml import etree
from lxml.builder import E

from pygments import highlight
from pygments.formatters import SvgFormatter
from pygments.lexers import PythonLexer

from .base import StylizedElement
from ..pygments_style import JupyterLabLightStyle


class Code(StylizedElement):
    
    def __init__(self, text, lexer=PythonLexer, pygments_style=JupyterLabLightStyle, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.lexer = lexer
        self.pygments_style = pygments_style
        
    def build(self, style):
        formatter = SvgFormatter(style=self.pygments_style, nowrap=True, fontsize=f"{style.fontsize}px")
        cellcode = highlight(self.text, self.lexer(), formatter)
        self.width = style.width
        self.height = formatter.yoffset + len(self.text.split("\n")) * formatter.ystep
        self.element = E.g(
            E.rect({
                'x': '0', 'y': '0', 'width': f'{self.width}', 'height': f'{self.height}',
                'fill': 'rgb(245, 245, 245)', 'stroke': ''
            }),
            E.g(
                etree.fromstring(f'<g>{cellcode}</g>', parser=etree.XMLParser(recover=True)), {
                    'transform': f'translate({style.code_padding} {style.code_padding})',
                    'font-family': 'monospace', 'font-size': f'{style.fontsize}px'
                }
            )
        )
        
    def __repr__(self):
        return f'Code({self.text!r})'
