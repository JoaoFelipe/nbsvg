from lxml.builder import E
from .base import StylizedElement
from .code import Code
from .markdown import Markdown
from .group import GroupSequence
from .output import display_data, stream_output, Error
from .text import Text
from .image import SVGGroup


def inout(number, ey, color, style, text=""):
    inoutpositiony = getattr(style, 'inoutpositiony', style.fontsize + ey)
    return E.g(
        E.g(
            E.text(
                E.tspan(f"{text}[{number}]:", {'fill': f"{color}"}),
                {
                    'x': f'{style.input_width - 3}',
                    'y': f'{inoutpositiony}',
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
        style.input_width += 25 if style.showtext else 0
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
        style.input_width += 25 if style.showtext else 0
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


class Cell(StylizedElement):
    
    def __init__(self, cell, **kwargs):
        super().__init__(**kwargs)
        self.cell = cell
        self._replace_cell = None
        self._replace_input = None
        self._remove_input = False
        self._replace_outputs = None
        self._remove_outputs = False
        self._replace_result = None
        self._replace_display = None
        self._replace_execution_count = None
        self._result_kwargs = {}
        self._display_kwargs = {}
        self.result = None
        
    def replace_cell(self, component):
        self._replace_cell = component
        
    def replace_input(self, component):
        self._replace_input = component
        
    def remove_input(self):
        self._remove_input = True
    
    def replace_outputs(self, component):
        self._replace_outputs = component
        
    def remove_outputs(self):
        self._remove_outputs = True
        
    def replace_result(self, component):
        self._replace_result = component
        
    def replace_display(self, component):
        self._replace_display = component
        
    def result_kwargs(self, kwargs):
        self._result_kwargs = kwargs
        
    def display_kwargs(self, kwargs):
        self._display_kwargs = kwargs
    
    def replace_execution_count(self, ec):
        self._replace_execution_count = ec

    def build(self, style):
        cell_type = self.cell.get('cell_type', '')
        source = self.cell.get('source', '')
        if self._replace_cell:
            result = self._replace_cell.do_build(style)
        elif cell_type == 'markdown':
            result = Markdown(source).do_build(style)
        elif cell_type == 'code':
            result = GroupSequence(group_margin=0)
            execution_count = self._replace_execution_count or self.cell.get('execution_count', ' ') or ' '
            cell_input = self._replace_input or CellInput(execution_count, source)
            if not self._remove_input:
                result.add(cell_input)
            if not self._remove_outputs:
                if self._replace_outputs:
                    result.add(self._replace_outputs)
                else:
                    for output in self.cell.get('outputs', []):
                        output_type = output.get('output_type', '')
                        if output_type == 'execute_result':
                            result.add(self._replace_result or CellOutput(
                                execution_count, 
                                display_data(output.get('data', {}), **self._result_kwargs)
                            ))
                        elif output_type == 'stream':
                            result.add(self._replace_display or CellDisplay(stream_output(output)))
                        elif output_type == 'display_data':
                            result.add(self._replace_display or CellDisplay( 
                                display_data(output.get('data', {}), **self._display_kwargs)
                            ))
                        elif output_type == 'error':
                            result.add(CellDisplay(Error(output)))
            result = result.do_build(style)
        else:
            result = Text(source).do_build(style)
        self.result = result
        self.element = result.element
        self.width = result.width
        self.height = result.height
    
    def __repr__(self):
        return f'Cell({self.cell!r})'


def ellipsis():
    return CellDisplay(SVGGroup(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" data-icon="ui-components:ellipses"><g xmlns="http://www.w3.org/2000/svg" class="jp-icon3" fill="#616161"><circle cx="5" cy="12" r="2"></circle><circle cx="12" cy="12" r="2"></circle><circle cx="19" cy="12" r="2"></circle></g></svg>',
        default_height=24
    )).translate(-6, 0)
