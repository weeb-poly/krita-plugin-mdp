from krita import Krita

from .mdp_plugin import MdpExtension

Krita.addExtension(MdpExtension(Krita.instance()))
