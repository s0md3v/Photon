import re
import importlib

from core.values import var
from core.utils import reader

def load_modules(phase, **kwargs):
    if var['modules']:
        for module in var['modules']:
            content = reader('./modules/' + module + '.py', string=True)
            phaseMatch = re.search(r'[\'"]phase[\'"] : [\'"]%s[\'"]' % phase, content)
            if phaseMatch:
                function_string = 'modules.' + module + '.' + module
                mod_name, func_name = function_string.rsplit('.',1)
                mod = importlib.import_module(mod_name)
                func = getattr(mod, func_name)
                func(kwargs)
