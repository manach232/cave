import os
import jinja2
from .volume import Volume


class Pool():
    """
        libvirt Pool (only dir-pools supported for now)
        Args:
            name: name of the pool
            path: the host path to the directory, directory has to exist
    """
    RELATIVE_TEMPLATE_PATH = "pool.jinja.xml"

    def __init__(self, name: str, path: str, libvirt_pool=None):
        self.name = name
        self.path = path
        self.libvirt_pool = libvirt_pool

    def _get_config(self):
        config = {
            "name": self.name,
            "path": self.path,
        }

        return config

    def create(self, conn):
        template_path = f"{os.path.dirname(
            __file__)}/{Pool.RELATIVE_TEMPLATE_PATH}"
        with open(template_path, "r") as f:
            template = jinja2.Template(f.read())
            self.libvirt_pool = conn.storagePoolDefineXML(
                template.render(self._get_config())
            )
            self.libvirt_pool.create()

    def create_volume(self, name: str, capacity, base_img=None, format="qcow2"):
        """
            Create a volume inside this pool
            Args:
                name: the name of the volume
                capacity: the size of the volume in GiB
                base_img: None or path to the qcow2 base image.
                format: format of the volume, if not qcow2 base_image cannot be used.
        """
        if not self.libvirt_pool:
            raise Exception("cannot create volume from pool that has not been created yet")
        volume_path = f"{self.path}/{name}"
        vol = Volume(name, volume_path,
                     capacity=capacity, pool_name=self.name, base_img=base_img, format=format)
        vol.create(self.libvirt_pool)
        return vol

    @staticmethod
    def destroy_by_name(conn, name):
        pool = conn.storagePoolLookupByName(name)
        for vol in pool.listAllVolumes():
            vol.delete()
        pool.destroy()
        pool.undefine()
