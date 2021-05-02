import re
import textwrap

from itertools import zip_longest

from lxml import etree
from lxml.builder import E
from .base import StylizedElement
from .group import GroupSequence

class Text(StylizedElement):
    
    def __init__(self, text, color='black', **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.color = color

    def build(self, style):
        fontsize = style.fontsize
        self.element = E.g({
            'font-family': f'{style.fontfamily}', 
            'font-size': f'{fontsize}'
        })
        #spacehack = True
        ystep = fontsize + 5
        lines = self.text.split('\n')
        self.width = 0
        for yi, line in enumerate(lines):
            self.width = max(self.width, len(line) * fontsize * style.fontwidth_proportion)
            #if spacehack:
            #    line = line.expandtabs().replace(' ', '&#160;')
            self.element.append(E.text(
                *self.interp_ansi(line),
                {'x': '0', 'y': f'{fontsize + ystep * yi}', 'text-anchor': style.textanchor,
                 '{http://www.w3.org/XML/1998/namespace}space': 'preserve'}
            ))
        self.height = len(lines) * ystep
        
    def interp_ansi(self, line):
        intensity_map = {
            0: {},
            1: {'font-weight': 'bold'},
        }
        color_map = {
            30: {'fill': 'black'}, # black
            0: {'fill': self.color}, # black
            31: {'fill': 'rgb(187, 0, 0)'}, # red
            32: {'fill': 'rgb(0, 187, 0)'}, # green
            33: {'fill': 'rgb(187, 187, 0)'}, # yellow
            34: {'fill': 'rgb(0, 0, 187)'}, # blue
            35: {'fill': 'rgb(187, 0, 187)'}, # magenta
            36: {'fill': 'rgb(0, 187, 187)'}, # cyan
            37: {'fill': 'rgb(187, 187, 187)'}, # white
        }

        parse = re.split(r'\x1b\[([0-9;]*)m',line)
        it = iter(parse)
        result = [E.tspan(next(it), {'fill': self.color})]

        for control, text in zip_longest(it, it):
            control = list(map(int, control.split(';')))
            control = [0] * (2 - len(control)) + control
            intensity, color = control
            attr = {**intensity_map.get(intensity, {}), 
                    **color_map.get(color, {'fill': self.color})}
            result.append(E.tspan(text, attr))
        
        return result

    def __repr__(self):
        return f'Text({self.text!r})'


class CodeSpan(StylizedElement):
            
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def build(self, style):
        text = self.text
        if isinstance(text, str):
            text = Text(text)
        text = text.do_build(style)
        self.element = E.g(
            E.rect({
                'x': '0', 'y': '0', 'width': f'{text.width}', 'height': f'{text.height}',
                'fill': 'rgb(245, 245, 245)'
            }),
            text.element
        )
        self.width = text.width
        self.height = text.height
        
    def __repr__(self):
        return f'CodeSpan({self.text!r})'


class Line(StylizedElement):
    
    def __init__(self, tspans, extra={}, **kwargs):
        super().__init__(**kwargs)
        self.tspans = tspans
        self.extra = extra
        
    def build(self, style):
        self.width = 0
        self.height = style.fontsize
        
        self.element = E.g({
            'font-family': f'{style.fontfamily}', 
            'font-size': f'{style.fontsize}', **self.extra
        })
        text = E.text({
            'x': '0', 'y': '0', 
            '{http://www.w3.org/XML/1998/namespace}space': 'preserve'
        })
        added = False
        for tspan in self.tspans:
            if isinstance(tspan, TSpan):
                added = True
                tspan = tspan.do_build(style)
                text.append(tspan.element)
            else:
                if added:
                    self.element.append(text)
                tspan = tspan.translate(self.width, -style.fontsize, add=True).do_build(style)
                self.width += tspan.width
                if added:
                    text = E.text({
                        'x': f'{self.width}', 'y': '0', 
                        '{http://www.w3.org/XML/1998/namespace}space': 'preserve'
                    })
                    added = False
                self.element.append(tspan.element)
            self.width += tspan.width
            self.height = max(self.height, tspan.height)
        if added:
            self.element.append(text)
    
        
        self.height += 5
        
    def __repr__(self):
        return f'Line({self.tspans!r}, extra={self.extra})'


class TSpan(StylizedElement):
    
    def __init__(self, text, attr={'fill': 'black'}, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.attr = attr
        
    def build(self, style):
        self.width = len(self.text) * style.fontsize * style.fontwidth_proportion
        self.height = style.fontsize
        self.element = E.tspan(self.text, self.attr)

    def __repr__(self):
        return f'TSpan({self.text!r}, attr={self.attr})'


class LineBreak(TSpan):
    
    def __init__(self, **kwargs):
        super().__init__("", attr={}, **kwargs)
    
    def __repr__(self):
        return 'LineBreak()'


def breakgroup(line, pos=0, result="", attrib={}, mappos=[], mapattr=[]):
    pos = 0
    mappos = []
    mapattr = []
    result = ""
    current_attr = {}
    for item in line:
        if isinstance(item, TSpan):
            if item.attr != current_attr:
                mappos.append(pos)
                mapattr.append(item.attr)
                current_attr = item.attr
            pos += len(item.text)
            result += item.text
        else:
            mappos.append(pos)
            mapattr.append(item)
            result += "\1"
            pos += 1
            mappos.append(pos)
            mapattr.append(current_attr)
            
    mappos.append(pos)
    mapattr.append({})
    return pos, result, mappos, mapattr


def breakgroup_to_lines(line, width):
    pos, result, mappos, mapattr = breakgroup(line)
    lines = textwrap.wrap(result, width=width, drop_whitespace=False)
    nexti = 1
    cpos = mappos[0]
    cattr = mapattr[0]
    npos = mappos[nexti]
    remaining = npos - cpos
    new_lines = GroupSequence()
    for line in lines:
        new_line = GroupSequence()
        nline = line.lstrip(' ')
        cpos += len(line) - len(nline)
        remaining = npos - cpos
        line = nline
        linesize = len(line)
        while linesize > remaining:
            subline = line[:remaining]
            if subline == "\1":
                new_line.add(cattr)
            else:
                new_line.add(TSpan(subline, cattr))
            linesize -= len(subline)
            line = line[remaining:]
            cpos += len(subline)
            cattr = mapattr[nexti]
            nexti += 1
            npos = mappos[nexti]
            remaining = npos - cpos
        if remaining >= linesize:
            subline = line
            if subline == "\1":
                new_line.add(cattr)
            else:
                new_line.add(TSpan(subline, cattr))
            cpos += len(subline)
            remaining = npos - cpos
        new_lines.add(new_line)
    return new_lines

def flat_tspan(text, attr={}):
    if isinstance(text, GroupSequence):
        result = GroupSequence()
        for item in text:
            if isinstance(item, GroupSequence):
                for subitem in flat_tspan(item, attr):
                    result.add(subitem)
            elif isinstance(item, TSpan):
                item.attr = {**item.attr, **attr}
                result.add(item)
            elif isinstance(item, StylizedElement):
                result.add(item)
            else:
                raise TypeError(f"Invalid type for {item}. Expected StylizedElement")
        return result
    if isinstance(text, TSpan):
        text.attr = {**text.attr, **attr}
        return text
    return TSpan(text, attr)


def split_by_linebreak(group):
    placeholder = GroupSequence()
    for item in group:
        if isinstance(item, LineBreak):
            yield placeholder
            placeholder = GroupSequence()
        else:
            placeholder.add(item)
    yield placeholder
    

def breaktext(text_e, pos=0, result="", attrib={}, mappos=[], mapattr=[]):
    for child in text_e.xpath("child::node()"):
        if hasattr(child, 'tag'):
            pos, result, mappos, mapattr = breaktext(
                child, pos=pos, result=result,
                attrib={**attrib, **child.attrib},
                mappos=mappos, mapattr=mapattr
                
            )
        else:
            ctex = str(child)
            mappos.append(pos)
            mapattr.append(attrib)
            pos += len(ctex)
            result += ctex
    return pos, result, mappos, mapattr


def breaktext_to_lines(text, width):
    temp = f'<temp>{text}</temp>'
    text_e = etree.fromstring(temp)
    pos, result, mappos, mapattr = breaktext(text_e, attrib={'fill': 'black'})
    mappos.append(pos)
    mapattr.append({})
    lines = textwrap.wrap(result, width=15, drop_whitespace=False)
    nexti = 1
    cpos = mappos[0]
    cattr = mapattr[0]
    npos = mappos[nexti]
    remaining = npos - cpos
    new_lines = []
    for line in lines:
        new_line = []
        nline = line.lstrip(' ')
        cpos += len(line) - len(nline)
        remaining = npos - cpos
        line = nline
        linesize = len(line)
        while linesize > remaining:
            subline = line[:remaining]
            new_line.append(E.tspan(subline, cattr))
            linesize -= len(subline)
            line = line[remaining:]
            cpos += len(subline)
            cattr = mapattr[nexti]
            nexti += 1
            npos = mappos[nexti]
            remaining = npos - cpos
        if remaining >= linesize:
            subline = line
            new_line.append(E.tspan(subline, cattr))
            cpos += len(subline)
            remaining = npos - cpos
        new_lines.append(new_line)
    return new_lines
