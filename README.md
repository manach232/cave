# Cave

**cave** is a Python-based automation toolkit for automated provisioning virtual infrastructure.  
Define your virtual infrastructure using code, cave handles the rest.  
Can be especially useful for more complex red-teaming training environments.  

Cave is still a prototype, use with caution.  
It is heavily worked on right now, stuff will change.  

## Features

* Supports both linux and windows
* Automated provisioning of virtual machines
* Automated provisioning of networks
* Automated configuration of network interfaces
* Automated installation of ssh
* Python API
---


## Use Cases
* use in conjunction with ansible to build a full-fledged cyber range
* quick and easy setup for testing environments

---
## Example topology
![example topology image](./assets/example_topology.drawio.png)

---

## Getting Started

You will need a Linux machine as your libvirt virtualisation host.
You can use whatever distro you like, cave was tested and will be tested using debian.

### Install libvirt
* Install libvirt (debian) `apt install --no-install-recommends qemu-system libvirt-clients libvirt-daemon-system`
* Install qemu-img `apt install qemu-utils`
* Install dnsmasq `apt install dnsmasq`
* install software tpm and ovmf for windows 11/uefi `apt install swtpm stpm-tools ovmf`

In case you face selinux issues, a quick-fix might be disabling apparmor/selinux by setting "security_driver" to ["none"] in /etc/libvirt/qemu.conf. Then `systemctl restart libvirtd`  

* Setup routes to your cave host
In order to allow traffic for comunicating with the virtual infrastructure, you will need to setup routes.
Take an ipv4 range that you will later use to make the machines within your deployment accessible to your network.
The virtualisation host will act as a router/next hop for the virtual networks and machines.  
For an example, see [example topology](assets/example_topology.drawio.png)

* Create ssh key for root user

* Download images
Download ISOs of the windows versions you will need, tested are: Windows 10, Windows 11, Windows-Server 16 and newer  
If you need to use Windows11/Any windows with uefi, you need to make a small change to the iso to make it boot without user interaction <https://serverfault.com/questions/353826/windows-boot-iso-file-without-press-any-key>.  
Download cloud-init images of the linux distributions you will use. Ubuntu <https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img> is tested.

---

## Usage
See [example](test/test.py) for an example.  

### Setup
```python

CON_URI = f"qemu+ssh://root@{HOST}/system"

conn = libvirt.open(CON_URI)
range = Range(conn, SSH_URI, TMP_CLOUD_INIT_DIR, SSH_PUB, USERNAME, PASSWORD)
range.nuke_libvirt()
range.add_pool(POOL_NAME,REMOTE_POOL_DIR)
```

### Networks and Interfaces
```python

mngt = range.add_management_network(name="mngmt", 
                         ipv4="10.10.0.1", # ipv4 the libvirt host gets inside the network, it then acts as gateway
                         ipv4_subnet="255.255.255.0") # subnet mask

n1 = range.add_network(name="network1", 
                       ipv4="", 
                       ipv4_subnet="", 
                       mode="") # mode, "open" if the libvirt host should route to and from the network

i1 = Interface(mac="", # leave empty 
               network=n1, # what network the interface is attached to
               ipv4="10.10.1.2", # ipv4 address of the interface
               prefix_length=24, # subnet mask network bist
               is_mngmt=False) # wether or not this is a management interface e.g. is connected to a management network, mngmt interfaces will be detatched in the cleanup phase

im = Interface(mac="", 
               network=mngt, 
               ipv4="10.10.0.2", 
               prefix_length=24, 
               is_mngmt=True) 
```

### Virtual Machines
```python
ubuntu_img = f"{REMOTE_IMAGES_DIR}/{os.path.basename(UBUNTU_IMAGE)}"
ld = range.add_linux_domain(name="linux01", # internal name
                            hostname="lin01", 
                            base_image_path=ubuntu_img, # absolute path to the cloud-init base image on the libvirt host
                            interfaces=[i1, im], # list of interfaces
                            graphics_passwd="pw", # vnc password
                            disk_volume_size_gb=8, # size of the main disk in GB
                            memory=1024, # ram
                            vcpus=2, # virtual vpu cores
                            graphics_port="6000", # port on which the vnc server listens
                            graphics_auto_port="no", # choose port automatically, no if graphics_port is set
                            graphics_address="0.0.0.0", # on which ip/interface the vnc server should listen
                            default_gateway="10.10.1.1", # the range-internal default gateway
                            dns_server="1.1.1.1", # the range internal dns server
                            management_default_gateway="10.10.0.1") # the default gateway for the management interface
```
