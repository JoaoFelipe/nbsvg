from lxml.html import document_fromstring

from .table import DataframeTable
from .image import Image

def html_output(html, **kwargs):
    dom = document_fromstring(html)
    tables = dom.xpath("//table")
    if tables and tables[0].attrib.get('class') == 'dataframe':
        return DataframeTable(dom, **kwargs)
    import imgkit
    res = imgkit.from_string(html, False)
    return Image(res)
