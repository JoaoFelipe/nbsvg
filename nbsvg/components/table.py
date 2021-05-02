import textwrap

from lxml.builder import E
from lxml import etree

from .base import StylizedElement

def extract_df_data(dom):
    table = dom.xpath("//table")[0]
    header_rows = [i for i, _ in enumerate(table.xpath("//thead/tr"))]

    table_data = []
    for row in table.xpath('//tr'):
        table_row = []
        for col in row.xpath('th | td'):
            text = col.text or ''
            table_row.append({
                'value': text,
                'bold': col.tag == 'th',
                'lines': [text]
            })
        table_data.append(table_row)

    p_data = None
    findp = dom.xpath("//p")
    if findp:
        p_data = findp[0].text
    return header_rows, table_data, p_data


def get_column_sizes(table_data, style):
    max_col_size = [style.table_colpadding] * len(table_data[0])
    for row in table_data:
        for i, col in enumerate(row):
            for line in col['lines']:
                max_col_size[i] = max(
                    max_col_size[i],
                    style.getsizeintable(line, col['bold'])
                )
    return max_col_size


class Table(StylizedElement):

    def __init__(self, table_data, header_rows, rcol={}, rdata={}, **kwargs):
        super().__init__(**kwargs)
        self.table_data = table_data
        self.header_rows = header_rows
        self.rcol = rcol
        self.rdata = rdata

    def build(self, style):
        table_data = self.table_data
        header_rows = self.header_rows

        for (i, j), value in self.rdata.items():
            if isinstance(value, str):
                table_data[i][j]['lines'] = [value]
            elif isinstance(value, list):
                table_data[i][j]['lines'] = value
            else:
                table_data[i][j] = value

        
        col_sizes = get_column_sizes(table_data, style)
        for key, value in self.rcol.items():
            col_sizes[key] = value
        
        fontsize = style.table_fontsize
        self.element = E.g({
            'font-family': f'{style.table_fontfamily}', 
            'font-size': f'{fontsize}'
        })
        spacehack = False
        ystep = fontsize + 5
        
        self.width = sum(col_sizes) + 5
        
        dy = 5
        for i, row in enumerate(table_data):
            max_lines = max(len(col['lines']) for col in row)
            total_height = max_lines * ystep
            dx = 0
            if i % 2 == 0 and i not in header_rows:
                self.element.append(E.rect({
                   'x': '0', 'y': f'{dy}', 'fill': 'rgb(245, 245, 245)', 
                   'height': f'{total_height}', 'width': f'{self.width}'
                }))
            
            for j, col in enumerate(row):
                py = dy + (max_lines - len(col['lines'])) / 2 * ystep
                dx += col_sizes[j]
                for yi, line in enumerate(col['lines']):
                    if spacehack:
                        line = line.expandtabs().replace(' ', '&#160;')
                    self.element.append(E.text(
                        E.tspan(line, {'fill': 'black'}),
                        {'x': f'{dx}', 'y': f'{fontsize + py + ystep * yi}', 
                         '{http://www.w3.org/XML/1998/namespace}space': 'preserve',
                         'text-anchor': 'end', 'font-weight': 'bold' if col['bold'] else 'normal'}
                    ))
                
            dy += total_height
            if i == header_rows[-1]:
                self.element.append(E.rect({
                   'x': '0', 'y': f'{dy}', 'fill': 'rgb(222, 222, 222)', 
                   'height': '1', 'width': f'{self.width}'
                }))
                dy += 1
        self.height = dy

    def __repr__(self):
        return f'Table({self.table_data!r}, {self.header_rows!r}, rcol={self.rcol!r})'


class WrapTable(Table):

    def __init__(self, table_data, header_rows, rlen={}, rcol={}, rdata={}, **kwargs):
        super().__init__(table_data, header_rows, rcol=rcol, rdata=rdata, **kwargs)
        self.rlen = rlen

    def build(self, style):
        wraplen = {**self.wrap_columns(style), **self.rlen}
        for row in self.table_data:
            for j, col in enumerate(row):
                if j in wraplen:
                    col['lines'] = textwrap.wrap(col['value'], width=wraplen[j])
        super().build(style)

    def wrap_columns(self, style):
        col_sizes = get_column_sizes(self.table_data, style)
        avg_col_size = style.width / len(col_sizes)
        undersized_cols = sum(avg_col_size - x for x in col_sizes if x < avg_col_size)
        oversized_cols = [i for i, x in enumerate(col_sizes) if x > avg_col_size]
        available_space_for_oversized = undersized_cols + avg_col_size * len(oversized_cols)
        fix_oversized = []
        if oversized_cols:
            oversized_avg = available_space_for_oversized / len(oversized_cols)
            fix_oversized = [i for i, x in enumerate(col_sizes) if x > oversized_avg]
            fix_col_len = style.fontlen(oversized_avg, "table")
        return {j: fix_col_len for j in fix_oversized}

    def __repr__(self):
        return f'WrapTable({self.table_data!r}, {self.header_rows!r}, rlen={self.rlen!r}, rcol={self.rcol!r})'


class DataframeTable(StylizedElement):
    
    def __init__(self, dom, **kwargs):
        super().__init__(**kwargs)
        self.dom = dom

    def build(self, style):
        header_rows, table_data, p_data = extract_df_data(self.dom)
        table = WrapTable(table_data, header_rows, **self.kwargs).do_build(style)
        self.element = table.element
        self.width = table.width
        self.height = table.height
        if p_data:
            self.element.append(E.text(
                etree.XML(f'<tspan fill="black">{p_data}</tspan>'),
                {'x': '0', 'y': f'{style.table_fontsize + table.height}', 
                '{http://www.w3.org/XML/1998/namespace}space': 'preserve'}
            ))
            self.height += style.table_fontsize + 5

    def __repr__(self):
        return f'DataframeTable({self.dom!r})'
