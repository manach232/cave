from setuptools import setup, find_packages

project_folder = "cave"
with open('README.md') as f:
    long_desc = f.read()

setup(
    name='cave-infra',
    version='0.1.1',
    packages=find_packages(),
    license_files=['LICENSE.txt'],
    description='Automation toolkit for automated provisioning virtual infrastructure.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    install_requires=[
        "Jinja2==3.1.6",
        "libvirt-python==11.4.0",
        "MarkupSafe==3.0.2"
    ],
    url='https://github.com/sn0ja/cave/',
    author='sn0ja',
)
