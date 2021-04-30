"""Defines a pygments style based on the JupyterLab Light Style"""
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Text, Whitespace, Other, Literal, \
     Punctuation


class JupyterLabLightStyle(Style):
    """
    A pygments style using the values of JupyterLab CSS variables.
    It was created based on jupyterlab_pygments.JupyterStyle using the following snippet to access variables:
      %%javascript
      var style = getComputedStyle(document.body)
      element.append(style.getPropertyValue('--jp-varname'))
    
    Please, check the JupyterStyle docs to see the known impossibilities
    """

    default_style = ''
    background_color = '#f5f5f5'
    highlight_color = 'white'

    styles = {
        Text:                      '#212121',
        Whitespace:                '',
        Error:                     '#f00',
        Other:                     '',
        Comment:                   'italic #408080',
        Keyword:                   'bold #008000',
        Operator:                  'bold #aa22ff',
        Operator.Word:             '',
        Literal:                   '',
        Literal.Date:              '',
        String:                    '#ba2121',
        Number:                    '#080',
        Name:                      '',
        Generic:                   '',
        Punctuation:               '#05a'
    }
