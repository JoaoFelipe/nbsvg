from lxml.builder import E
from .base import StylizedElement
from .code import Code

def inout(number, ey, color, style, text=""):
    return E.g(
        E.g(
            E.text(
                E.tspan(f"{text}[{number}]:", {'fill': f"{color}"}),
                {
                    'x': f'{style.input_width - 3}',
                    'y': f'{style.fontsize + ey}',
                    '{http://www.w3.org/XML/1998/namespace}space': 'preserve',
                    'text-anchor': 'end'
                }
            ), {
                'font-family': 'monospace',
                'font-size': f'{style.fontsize}px'
            }
        )
    )


class CellInput(StylizedElement):
    
    def __init__(self, number, text, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.text = text

    def build(self, style):
        self.element = inout(
            self.number, 6 + 5, "#307fc1", style,
            text="In " if style.showtext else ""
        )
        code = Code(self.text).translate(style.input_width, 5)
        self.element.append(code.do_build(style, width=style.width - style.input_width).element)
        self.width = style.width
        self.height = code.height + 10

    def __repr__(self):
        return f'CellInput({self.number!r}, {self.text!r})'


class CellOutput(StylizedElement):
    
    def __init__(self, number, output, **kwargs):
        super().__init__(**kwargs)
        self.number = number
        self.output = output

    def build(self, style):
        self.element = inout(
            self.number, 0, "#bf5b3d", style,
            text="Out" if style.showtext else ""
        )
        output = self.output.translate(style.input_width + 7, 0)
        self.element.append(output.do_build(style, width=style.width - style.input_width).element)
        self.width = style.width
        self.height = output.height + 5

    def __repr__(self):
        return f'CellOutput({self.number!r}, {self.output!r})'


class CellDisplay(StylizedElement):
    
    def __init__(self, output, **kwargs):
        super().__init__(**kwargs)
        self.output = output

    def build(self, style):
        self.element = E.g()
        output = self.output.translate(style.input_width + 7, 0)
        self.element.append(output.do_build(style, width=style.width - style.input_width).element)
        self.width = style.width
        self.height = output.height

    def __repr__(self):
        return f'CellDisplay({self.output!r})'
