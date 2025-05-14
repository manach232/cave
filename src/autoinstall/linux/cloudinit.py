import jinja2
import os
import uuid
from ...domains.interface import Interface

class CloudInitUserConfig():
    RELATIVE_TEMPLATE_PATH = "cloud-init-user.jinja.yaml"
    CLOUDINIT_FILE_NAME = "user-data"

    def __init__(self, username: str, password: str, ssh_pub: str, hostname="ab"):
        self.username = username
        self.password = password
        self.ssh_pub = ssh_pub
        self.hostname = hostname

    def _get_config(self):
        config = {
            "username": self.username,
            "password": self.password,
            "ssh_pub": self.ssh_pub,
            "hostname": self.hostname
        }
        return config 

    def __repr__(self):
        template_path = f"{os.path.dirname(
            __file__)}/{CloudInitUserConfig.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            return template.render(self._get_config())

class CloudInitMetaData():
    RELATIVE_TEMPLATE_PATH = "cloud-init-meta.jinja.yaml"
    CLOUDINIT_FILE_NAME = "meta-data"

    def __init__(self,  hostname: str, instance_id=""):
        self.instance_id = instance_id if instance_id else str(uuid.uuid4())
        self.hostname = hostname

    def _get_config(self):
        config = {
            "instance_id": self.instance_id,
            "local_hostname": self.hostname
        }
        return config

    def __repr__(self):
        template_path = f"{os.path.dirname(
            __file__)}/{CloudInitMetaData.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            return template.render(self._get_config())

class CloudInitNetworkConfig():
    RELATIVE_TEMPLATE_PATH = "cloud-init-network.jinja.yml"
    CLOUDINIT_FILE_NAME = "network-config"

    def __init__(self,  interfaces: list[Interface], range_default_gateway:str, range_dns_server: str, management_default_gateway: str):
        self.interfaces = interfaces
        self.management_default_gateway = management_default_gateway
        self.range_default_gateway = range_default_gateway
        self.range_dns_server = range_dns_server

    def _get_config(self):
        config = {
            "interfaces": [[interface.mac, f"{interface.ipv4}/{interface.prefix_length}", interface.is_mngmt] for interface in self.interfaces],
            "management_default_gateway": self.management_default_gateway,
            "range_default_gateway": self.range_default_gateway,
            "range_dns_server": self.range_dns_server
        }
        return config

    def __repr__(self):
        template_path = f"{os.path.dirname(
            __file__)}/{CloudInitNetworkConfig.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            cont = template.render(self._get_config())
            return cont
