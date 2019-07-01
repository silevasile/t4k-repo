import os
import os.path
import xbmcaddon

__settings__ = xbmcaddon.Addon()
#disabled_files = os.listdir(os.path.join(os.path.dirname(__file__), 'disabled'))
__disabledtr__ = []
files = os.listdir(os.path.dirname(__file__))
__alltr__ = []
for filename in files:
    if not filename.startswith('__') and filename.endswith('.py'):
        if __settings__.getSetting(filename[:-3]) == 'false':
            __disabledtr__.append(filename[:-3])
        else:
            __alltr__.append(filename[:-3])
            
#__disabled__ = [filename[:-3] for filename in disabled_files if not filename.startswith('__') and filename.endswith('.py')]
