from distutils.util import strtobool
from xml.etree.ElementTree import Element

def getIccProfile(mdiApp: Element) -> str:
    icc_xml = mdiApp.find('./ICCProfiles')
    if icc_xml is None:
        return ""

    icc_enabled = strtobool(icc_xml.attrib.get('enabled', 'False'))
    if icc_enabled is not True:
        return ""

    # TODO: Extract icc profile from xml
    doc_icc = ""

    return doc_icc
