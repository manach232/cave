import subprocess
import tempfile
import os
import uuid
import logging

logger = logging.getLogger("default")

def send_file(ssh_uri: str, local_file_path: str, remote_file_path: str):
    """
        Creates target folder if it does not exist and moves file_path in it
    """
    subprocess.check_call(
        ["ssh", f"{ssh_uri}", "mkdir", "-p", os.path.dirname(remote_file_path)], stdout=subprocess.DEVNULL)
    subprocess.check_call(["scp", local_file_path, f"{ssh_uri}:{remote_file_path}"], stdout=subprocess.DEVNULL)

def create_and_push_cd(remote_path, ssh_connect_string, cdrom_files: dict, ):
    logger.debug(f"Creating iso file from files: {cdrom_files}")
    with Cdrom(files=cdrom_files) as cd:
        iso = cd
        logger.debug(f"sending iso file {cd}, to {remote_path} via {ssh_connect_string}") 
        send_file(ssh_connect_string, iso, remote_path)
    return remote_path

class Cdrom():
    """
        Class used to create iso disk image from files
        Context manager (with) is supported
        Args:
            files: a dict in the format {filename: file_content, filename2: file_content2}
        Example usage:
            with Cdrom({"mydisk.iso":"Hello World!"}) as tmp_file_path:
                print(tmp_file_path)

    """
    def __init__(self, files: dict[str,str]):
        self.files = files
    def _to_iso(self, iso_filename):
        subprocess.check_call(["genisoimage", "-output", os.path.join(self.dir.name, iso_filename), "-volid", "cidata", "-joliet", "-rock", "-input-charset", "utf-8", self.dir.name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def __enter__(self):
        self.dir = tempfile.TemporaryDirectory()

        for filename,content in self.files.items():
            with open(os.path.join(self.dir.name, filename), "w", newline="\r\n") as f:
                f.write(content)

        iso_filename = f"{uuid.uuid4()}.iso"
        self._to_iso(iso_filename)

        return os.path.join(self.dir.name, iso_filename)

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.dir.cleanup()


