import re
import textwrap

from lxml import etree
from lxml.builder import E
from .base import StylizedElement
from .group import GroupSequence

class Text(StylizedElement):
    
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def build(self, style):
        fontsize = style.fontsize
        self.element = E.g({
            'font-family': f'{style.fontfamily}', 
            'font-size': f'{fontsize}'
        })
        spacehack = True
        ystep = fontsize + 5
        lines = self.text.split('\n')
        self.width = 0
        for yi, line in enumerate(lines):
            self.width = max(self.width, len(line) * fontsize * style.fontwidth_proportion)
            if spacehack:
                line = line.expandtabs().replace(' ', '&#160;')
            self.element.append(E.text(
                etree.XML(self.interp_ansi(line)),
                #E.tspan(line, {'fill': 'black'}),
                {'x': '0', 'y': f'{fontsize + ystep * yi}', 
                 '{http://www.w3.org/XML/1998/namespace}space': 'preserve'}
            ))
        self.height = len(lines) * ystep
        
    def interp_ansi(self, line):
        # From: https://github.com/markrages/ansi_svg/blob/master/ansi_svg.py
        def rgb(r,g,b): return "#%02x%02x%02x"%(r,g,b)
        br_on = 255
        br_off = 85
        norm_on = 187

        colortab = {(0,30):rgb( br_off, br_off, br_off), # black
            (0,31):rgb(  br_on, br_off, br_off), # red
            (0,32):rgb( br_off,  br_on, br_off), # green
            (0,33):rgb(  br_on,  br_on, br_off), # yellow
            (0,34):rgb( br_off, br_off,  br_on), # blue
            (0,35):rgb(  br_on, br_off,  br_on), # magenta
            (0,36):rgb( br_off,  br_on,  br_on), # cyan
            (0,37):rgb(  br_on,  br_on,  br_on), # white
            (1,30):rgb(      0,      0,      0), # black
            (1,31):rgb(norm_on,      0,      0), # red
            (1,32):rgb(      0,norm_on,      0), # green
            (1,33):rgb(norm_on,norm_on,      0), # yellow
            (1,34):rgb(      0,      0,norm_on), # blue
            (1,35):rgb(norm_on,      0,norm_on), # magenta
            (1,36):rgb(      0,norm_on,norm_on), # cyan
            (1,37):rgb(norm_on,norm_on,norm_on)  # white
            }

        self.ansicolor = (0,0)
        ret = '<tspan fill="black">'

        # Look for 'm' command
        parse=re.split(r'\x1b\[([0-9;]*)m',line)
        
        while parse:
            ret += parse.pop(0)
            if not parse: 
                break
            csr = parse.pop(0)
            if not csr:
                args = []
            else:
                args = [int(a) for a in csr.split(';') if a]

            if len(args)==2:
                intensity, color = args
            elif len(args)==1:
                intensity, color = [0]+args
            else:
                intensity, color = 0,0
            

            if self.ansicolor != (intensity,color):
                if self.ansicolor != (0,0):
                    ret += '</tspan>'

                if (intensity,color) != (0,0):
                    try:
                        ret += f'<tspan fill="{colortab[(intensity, color)]}">'
                    except KeyError:
                        ret += f'<tspan id="unknown_{repr(intensity,color)}">'

                self.ansicolor = intensity,color

        ret += '</tspan>'
        self.ansicolor = (0,0)

        return ret

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
