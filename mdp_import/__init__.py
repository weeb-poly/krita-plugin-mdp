__all__ = [
    'neet',
    'weeb'
]

import os
import site

# Load site-packages
site_path = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.join(site_path, "site-packages"))

from . import neet
from . import weeb

# Add Krita extension if we're a plugin
try:
    from krita import Krita
except ImportError:
    pass
else:
    from .plugin import MdpExtension

    Krita.addExtension(MdpExtension(Krita.instance()))
