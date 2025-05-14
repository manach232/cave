import jinja2
from logging import getLogger
from ..os_types import OsType
import os
from libvirt import libvirtError
from .interface import Interface  

logger = getLogger("default")
class TemplatedLibvirtDomain():
    RELATIVE_FILTER_PATH = "filter.xml"
    FILTER_NAME = "deny-vm-to-host"

    def __init__(self, config: dict, template_str: str, name: str, interfaces: list[Interface], os_type: OsType):
        self.config = config
        self.jinja_template = jinja2.Template(template_str) 
        self.os_type = os_type
        self.libvirt_domain = None
        self.name = name
        self.interfaces = interfaces

    def define_filter_if_not_exists(self, conn):
        filter_path = f"{os.path.dirname(
            __file__)}/{TemplatedLibvirtDomain.RELATIVE_FILTER_PATH}"
        with open(filter_path, "r") as f:
            filter = f.read()
        try:
            conn.nwfilterDefineXML(filter)
        except libvirtError:
            if str(libvirtError) == "virNWFilterDefineXML() failed":
                pass
        
    def create(self, conn):
        self.define_filter_if_not_exists(conn)
        logger.debug(f"creating libvirt domain with config: {self.config} {self.jinja_template}")
        xml_content = self.jinja_template.render(self.config)
        self.libvirt_domain = conn.defineXML(xml_content)
        self.libvirt_domain.create()

    def to_dict(self):
        dict_interfaces = []
        for interface in self.interfaces:
            dict_interfaces.append({
                "mac": interface.mac,
                "network_name": interface.network.name,
                "ipv4": interface.ipv4,
                "is_mngmt": interface.is_mngmt
            })

        return {"name": self.name, "interfaces": dict_interfaces, "os_type":str(self.os_type)}
        
    def get_mngmt_ipv4(self):
        if len(self.interfaces) < 1:
            return ""
        return next(filter(lambda x: x.is_mngmt, self.interfaces)).ipv4

    @staticmethod
    def remove_interface_for_network_name(conn, name: str, network_name: str):
        libvirt_domain = conn.lookupByName(name)
        libvirt_domain.detachDeviceAlias(f"ua-{network_name}", 0x03)


