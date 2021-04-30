import mistune

from lxml.builder import E
from pygments import lexers

from .base import StylizedElement
from .glist import List
from .text import breakgroup_to_lines, split_by_linebreak, flat_tspan, breakgroup
from .text import CodeSpan, Line, TSpan, LineBreak
from .group import GroupSequence, force_groupsequence
from .image import Image
from .html import HTML
from .table import WrapTable
from .code import Code

from .. import style

LEXER_MAP = {
    'bash': lexers.BashLexer,
    'html': lexers.HtmlLexer,
    'javascript': lexers.JavascriptLexer,
    'perl': lexers.PerlLexer,
    'python': lexers.PythonLexer,
    'ruby': lexers.RubyLexer,
    'tex': lexers.TexLexer,
    '': lexers.HtmlLexer,
}

class HRule(StylizedElement):
            
    def build(self, style):
        self.element = E.g(
            E.rect(
            {'x': '0', 'y': '1', 'width': f'{style.width}', 
             'height': '2', 'fill': 'rgb(220, 220, 220)'}
        ))
        self.width = style.width
        self.height = 4

    def __repr__(self):
        return 'HRule()'


class Quote(StylizedElement):
            
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text

    def build(self, style):
        text = self.text.translate(35, 0).do_build(style, width=style.width - 35)
        self.height = text.height + 5
        self.width = text.width + 35
        self.element = E.g(
            E.rect({
                'x': '23', 'y': '0', 'width': '4', 
                'height': f'{text.height}', 'fill': 'rgb(220, 220, 220)'
            }),
            text.element
        )

    def __repr__(self):
        return f'Quote({self.text!r})'        
    

class SVGRenderer(mistune.Renderer):
    
    def __init__(self, style):
        super().__init__()
        self.style = style
    
    def create_lines(self, lines, fontsize, fontfamily, extra={}):
        result = GroupSequence(group_margin=fontsize)
        for line in lines:
            result.add(Line(
                [tspan for tspan in line],
                fontsize=fontsize, fontfamily=fontfamily,
                extra=extra
            ))
        result.translate(0, fontsize // 2)
        return result
    
    def text(self, text):
        return flat_tspan(text, {'fill': 'black'})
    
    def emphasis(self, text):
        return flat_tspan(text, attr={'font-style': 'italic'})
        
    def double_emphasis(self, text):
        return flat_tspan(text, attr={'font-weight': 'bold'})
   
    def strikethrough(self, text):
        return flat_tspan(text, attr={'text-decoration': 'line-through'})

    def link(self, link, title, text):
        return flat_tspan(text or link, attr={'fill': 'rgb(25, 118, 210)'})
   
    def autolink(self, link, is_email):
        return self.link(link, "", "")
     
    def linebreak(self):
        return LineBreak()
    
    def newline(self):
        return LineBreak()
    
    def placeholder(self):
        return GroupSequence(group_margin=0)
    
    def paragraph(self, text):
        text = force_groupsequence(flat_tspan(text))
        nested_lines = [
            breakgroup_to_lines(
                line,
                self.style.fontlen(self.style.width, "p")
            ) for line in split_by_linebreak(text)
        ]
        lines = GroupSequence()
        for linegroup in nested_lines:
            for group in linegroup:
                lines.add(group)
        
        return self.create_lines(
            lines, self.style.p_fontsize,
            self.style.markdown_fontfamily,
        )
    
    def header(self, text, level, raw=None):
        fontsize = getattr(self.style, f"h{level}_fontsize")
        lines = breakgroup_to_lines(
            force_groupsequence(flat_tspan(text)),
            self.style.fontlen(self.style.width, f"h{level}")
        )
        return self.create_lines(
            lines, fontsize, 
            self.style.markdown_fontfamily,
            extra={
                "font-weight": "bold"
            }
        )
        
    def block_code(self, code, lang=None):
        if lang not in LEXER_MAP:
            lang = ''
        lexer = LEXER_MAP[lang]      
        return Code(code, lexer=lexer)

    def block_quote(self, text):
        return Quote(text)
        
    def block_text(self, text):
        return text
        
    def hrule(self):
        return HRule()
    
    def thematic_break(self):
        return self.hrule()
    
    def block_html(self, html):
        return HTML(html)
        
    def inline_html(self, html):
        return HTML(html)
        
    def image(self, src, alt="", tilte=None):
        return Image(src)

    def codespan(self, text):
        return CodeSpan(text)

    def table_cell(self, text, align=None, header=False):
        # Simplyfing table to use plain text
        text = force_groupsequence(flat_tspan(text))
        pos, result, mappos, mapattr = breakgroup(text)
        return {
            'value': result,
            'lines': [result],
            'bold': header
        }
    
    def table_row(self, text):
        return [cell for cell in text]
    
    def table(self, header, body):
        hdata = [row for row in header]
        bdata = [row for row in body]
        header_rows = range(len(hdata))
        table_data = hdata + bdata
        return WrapTable(table_data, header_rows)
    
    def list_item(self, text):
        return text
    
    def list(self, body, ordered=True):
        body = force_groupsequence(flat_tspan(body))
        lines = GroupSequence()
        for tspan in body:
            lines.add(GroupSequence().add(tspan))
        result = self.create_lines(
            lines, self.style.p_fontsize,
            self.style.markdown_fontfamily,
        )
        return List(result, ordered)
    
    # ToDo:
    # escape(self, text)
    # footnote_ref(self, key, index)
    # footnote_item(self, key, text)
    # footnotes(self, text)


class Markdown(StylizedElement):

    def __init__(self, markdown, **kwargs):
        super().__init__(**kwargs)
        self.markdown = markdown

    def build(self, style):
        renderer = SVGRenderer(style=style)
        markdownfn = mistune.Markdown(renderer=renderer, escape=False)
        obj = markdownfn(self.markdown).do_build(style)
        self.element = obj.element
        self.width = obj.width
        self.height = obj.height

    def __repr__(self):
        return f'Markdown({self.markdown!r})'
