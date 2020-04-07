import os
import os.path
import xbmcaddon

__settings__ = xbmcaddon.Addon()
#disabled_files = os.listdir(os.path.join(os.path.dirname(__file__), 'disabled'))
__disabled__ = []
files = os.listdir(os.path.dirname(__file__))
__all__ = []
for filename in files:
    if not filename.startswith('__') and filename.endswith('.py'):
        if __settings__.getSetting(filename[:-3]) == 'false':
            __disabled__.append(filename[:-3])
        else:
            __all__.append(filename[:-3])
            
#__disabled__ = [filename[:-3] for filename in disabled_files if not filename.startswith('__') and filename.endswith('.py')]
