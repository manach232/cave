import os 
import ipaddress
import jinja2
import re

class Network(object):
    """
        
        Args:
            conn: libvirt connection object
            mode: set this to empty string for isolated virt-network
            ipv4: first ip in the network, not !net-id!, if dhcp or dns is used this will be the address of the dhcp/dns server
            ipv4_subnetmask: subnetmask e.g. 255.255.255.0
            ipv6: first ipv6 in ipv6 range of network
            ipv6_prefix: e.g. 64

    """
    RELATIVE_TEMPLATE_PATH = "network.jinja.xml"

    def __init__(self, name: str,  host_isolated=None, ipv4="", ipv4_subnet="", isolate_guests=None, ipv6="", ipv6_prefix="64", mode="", ingress_route_subnet=None, ingress_route_gateway=None ):
        self.name = name
        self.mode = mode
        self.ipv4 = ipv4
        self.ipv4_subnet = ipv4_subnet
        self.ipv6 = ipv6
        self.ipv6_prefix = ipv6_prefix
        self.host_isolated = True if host_isolated else False 
        self.isolate_guests = "yes" if isolate_guests else "no"
        self.host_mac = None
        self.ingress_route_subnet = ipaddress.ip_network(ingress_route_subnet) if ingress_route_subnet else None
        self.ingress_route_gateway = ingress_route_gateway if ingress_route_gateway else None

    def _get_config(self) -> dict:
        config = {
            "name": self.name,
            "mode": self.mode,
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "ipv4_subnetmask": self.ipv4_subnet,
            "ipv6_prefix": self.ipv6_prefix,
            "host_isolated": self.host_isolated,
            "isolate_guests": self.isolate_guests,
            "ingress_route_subnet_ip":  str(self.ingress_route_subnet.network_address) if self.ingress_route_subnet else None,
            "ingress_route_subnet_prefix_length": str(self.ingress_route_subnet.prefixlen) if self.ingress_route_subnet else None,
            "ingress_route_gateway": self.ingress_route_gateway 
            
        }
        return config

    def to_dict(self):
        return {"name":self.name,
                "mode":self.mode}

    def get_host_mac_from_xml(self):
        #<mac address='52:54:00:0e:4b:74'/>
        assert self.libvirt_network
        matches = re.search(r"<mac address='(?P<mac>.*)'/>", self.libvirt_network.XMLDesc())
        if not matches:
            raise Exception(f"no mac found in in network definition for {self.name} unable to set isolate host iptables rules")
        return matches.group('mac')

    def create(self, conn):
        # lookupByName throws if the name is not found
        template_path = f"{os.path.dirname(
            __file__)}/{Network.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            xml_content = template.render(self._get_config())
            self.libvirt_network = conn.networkDefineXML(xml_content)
            self.libvirt_network.create()
            self.host_mac = self.get_host_mac_from_xml()
    
    def destroy(self):
        assert self.libvirt_network
        self.libvirt_network.destroy()

    @staticmethod
    def destroy_by_name(conn, name):
        network = conn.networkLookupByName(name)
        network.destroy()
        network.undefine()
        
