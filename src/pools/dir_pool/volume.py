import os
import jinja2

class Volume():
    """
        Libvirt volume
        backing image (base_img) and volume only support qcow2 format for now.
        Args:
            pool: the pool in which the vol should be created
            name: name of the volume
            path: host path of the image file
            capacity: the initial size of the volume on the host
            base_img: name of qcow2 image to use as base, this is copy on write
    """
    RELATIVE_TEMPLATE_PATH = "volume.jinja.xml"

    def __init__(self, name: str, path: str, capacity, pool_name:str, base_img=None, format="qcow2"):
        self.name = name
        self.path = path
        self.capacity = capacity
        self.base_img = base_img
        self.format = format
        self.pool_name = pool_name

    def _get_config(self) -> dict:
        config = {
            "name": self.name,
            "capacity": self.capacity,
            "path": self.path,
            "base_img": self.base_img,
            "format": self.format
        }
        return config

    def create(self, libvirt_pool):
        template_path = f"{os.path.dirname(
            __file__)}/{Volume.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            libvirt_pool.createXML(
                template.render(self._get_config()))
