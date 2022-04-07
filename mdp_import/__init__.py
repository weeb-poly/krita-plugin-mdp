from krita import Krita

from .plugin import MdpExtension

Krita.addExtension(MdpExtension(Krita.instance()))
