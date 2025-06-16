from ..templated_libvirt_domain import TemplatedLibvirtDomain
from ..interface import Interface
import os, uuid
from ...os_types import OsType

class WindowsDomain(TemplatedLibvirtDomain):
    RELATIVE_TEMPLATE_PATH = "domain_windows.jinja.xml"
    def get_template_str(self):
        template_path = f"{os.path.dirname(
            __file__)}/{WindowsDomain.RELATIVE_TEMPLATE_PATH}"

        with open(template_path, "r") as f:
            template_content = f.read()

        return template_content
            
    def __init__(self, name: str, disk_volume, boot_iso, interfaces: list[Interface], graphics_passwd: str, cdrom: str, memory: int, vcpus: int, graphics_port: str, graphics_auto_port: str, graphics_address: str, os_type:OsType):
        assert not (graphics_port and (graphics_auto_port == "yes"))
        config = {
            "name": name,
            "memory": memory,
            "uuid": uuid.uuid4(),
            "vcpus": vcpus,
            "cdrom": cdrom,
            "boot_iso": boot_iso,
            "interfaces": [{"mac": x.mac, "net_name" : x.network.name, "net_host_mac": x.network.host_mac, "net_host_isolated": x.network.host_isolated} for x in interfaces],
            "disk_volume": {
                "format": disk_volume.format,
                "name": disk_volume.name,
                "base_img": disk_volume.base_img,
                "pool_name": disk_volume.pool_name
            },
            "graphics_port": graphics_port,
            "graphics_passwd": graphics_passwd,
            "graphics_auto_port": graphics_auto_port,
            "graphics_address": graphics_address
        }

        super().__init__(config, self.get_template_str(), name, interfaces, os_type)

        self.name = name
        self.disk_volume = disk_volume
        self.interfaces = interfaces
        self.graphics_passwd = graphics_passwd
        self.cdrom = cdrom
        self.boot_iso = boot_iso
        self.memory = memory
        self.vcpus = vcpus
        self.graphics_port = graphics_port
        self.graphics_auto_port = graphics_auto_port
        self.graphics_address = graphics_address 
        self.os_type = os_type


    def create(self, conn):
        super().create(conn)

    @staticmethod
    def remove_cdrom(conn, name):
        libvirt_domain = conn.lookupByName(name)
        # TODO: do proper xml parsing, don not hardcode ua-config-cdrom
        target = f"""
            <disk type='file' device='cdrom'>
                <driver name='qemu' type='raw'/>
                <backingStore/>
                <target dev='hdc' bus='sata'/>
                <readonly/>
                <alias name='ua-config-cdrom'/>
            </disk>
        """
        libvirt_domain.updateDeviceFlags(target, 0x3)

