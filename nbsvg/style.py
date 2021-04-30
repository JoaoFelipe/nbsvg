"""Define base style for components"""
from copy import copy

class Style:
    
    old = []
    input_width = 35
    width = 700
    fontsize = 10
    showtext = False
    code_padding = 7
    group_margin = 10
    fontfamily = 'monospace'
    fontwidth_proportion = 0.6
    
    table_bold_fontwidth_proportion = 0.67
    table_fontwidth_proportion = 0.6
    table_colpadding = 5
    table_fontsize = 9
    table_oversize_proportion = 1.3
    table_fontfamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
    
    markdown_fontfamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"'
    p_fontsize = 9
    p_oversize_proportion = 1.3
    p_fontwidth_proportion = 0.6
    
    h1_fontsize = 19
    h1_oversize_proportion = 1.3
    h1_fontwidth_proportion = 0.6
    
    h2_fontsize = 16
    h2_oversize_proportion = 1.3
    h2_fontwidth_proportion = 0.6
    
    h3_fontsize = 13
    h3_oversize_proportion = 1.3
    h3_fontwidth_proportion = 0.6
    
    h4_fontsize = 11
    h4_oversize_proportion = 1.3
    h4_fontwidth_proportion = 0.6
    
    h5_fontsize = 9
    h5_oversize_proportion = 1.3
    h5_fontwidth_proportion = 0.6
    
    h6_fontsize = 8
    h6_oversize_proportion = 1.3
    h6_fontwidth_proportion = 0.6
    
    
    
    def apply(self, kwargs, this=True):
        result = self if this else copy(self)
        result.old.append({})  
        for key, value in kwargs.items():
            result.old[-1][key] = getattr(self, key, None)
            setattr(result, key, value)
        return result
        
    def undo(self):
        old = self.old.pop()
        for key, value in old.items():
            setattr(self, key, value)
            
    def getsizeintable(self, text, bold):
        prop = self.table_fontwidth_proportion
        if bold:
            prop = self.table_bold_fontwidth_proportion
        return len(text) * prop * self.table_fontsize + self.table_colpadding

    def fontlen(self, width, name):
        return int(
            width
            // (getattr(self, f'{name}_fontsize') * getattr(self, f'{name}_fontwidth_proportion'))
            * getattr(self, f'{name}_oversize_proportion')
        )

class PilStyle(Style):
    
    fonttype = "SEGOEUI.TTF"
    bold_fonttype = "SEGOEUIB.TTF"
    
    def getsizeintable(self, text, bold):
        from PIL import ImageFont
        cfont = ImageFont.truetype(self.fonttype, self.table_fontsize)
        if bold:
            cfont = ImageFont.truetype(self.bold_fonttype, self.table_fontsize)
        return cfont.getsize(text)[0] + self.table_colpadding


STYLE = Style()
