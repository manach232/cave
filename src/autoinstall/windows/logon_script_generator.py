from ... domains.interface import Interface
import jinja2
import os

RELATIVE_SCRIPT_PATH = "first_logon_script.ps1"

def get_logon_script(interfaces: list[Interface], ssh_pub: str, range_default_gateway: str, range_dns_server: str, management_default_gateway: str):
     nets = [] 
     for interface in interfaces:
         interface_gw = ""
         interface_dns = ""
         if not interface.is_mngmt:
             interface_gw = range_default_gateway
             interface_dns = range_dns_server
         else:
             interface_gw = management_default_gateway
             interface_dns = management_default_gateway

         nets.append([interface.mac, interface.ipv4, interface.prefix_length, interface_gw, interface_dns, interface.is_mngmt])

     config = {
         "interfaces": nets,
         "ssh_pub": ssh_pub
     }

     script_path = f"{os.path.dirname(
         __file__)}/{RELATIVE_SCRIPT_PATH}"

     with open(script_path, "r") as f:
         template = jinja2.Template(f.read())
         cont = template.render(config)
         return cont

