import jinja2
import os
from ..logon_script_generator import get_logon_script

class AutounattendGPT():
    """
        Args:
            Interfaces: [[mac, ipv4, prefix_length]] used to assign static ip to interfaces differentiating them by mac
    """
    RELATIVE_TEMPLATE_PATH = "autounattend_gpt.jinja.xml"
    RELATIVE_SCRIPT_PATH = "../first_logon_script.ps1"
    def __init__(self, username: str, ssh_pub: str, password, hostname: str, interfaces, management_default_gateway: str, range_default_gateway: str, range_dns_server: str, product_key: str):
        self.username = username
        self.ssh_pub = ssh_pub
        self.hostname = hostname
        self.v4release = True
        self.v6release = True
        self.password = password
        self.product_key = product_key
        self.interfaces = interfaces
        self.management_default_gateway = management_default_gateway
        self.range_default_gateway = range_default_gateway
        self.range_dns_server = range_dns_server

    def _get_config(self):
        config = {
            "username": self.username,
            "hostname": self.hostname,
            "v4release": self.v4release,
            "v6release": self.v6release,
            "password": self.password,
            "product_key": self.product_key,
            "interfaces": self.interfaces,
            "first_logon_script": get_logon_script(self.interfaces, 
                                                   self.ssh_pub, 
                                                   self.range_default_gateway, 
                                                   self.range_dns_server, 
                                                   self.management_default_gateway)
        }
        return config

    def __repr__(self):
        template_path = f"{os.path.dirname(
            __file__)}/{AutounattendGPT.RELATIVE_TEMPLATE_PATH}"

        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            cont = template.render(self._get_config())
            return cont
