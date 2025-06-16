from setuptools import setup, find_packages

project_folder = "cave"
with open('README.md') as f:
    long_desc = f.read()
with open("requirements.txt") as f:
    dependencies = map(lambda x: x.replace("\n",""), f.readlines())

setup(
    name='cave-infra',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    description='Automation toolkit for automated provisioning virtual infrastructure.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    install_requires=dependencies,
    url='https://github.com/sn0ja/cave/',
    author='sn0ja',
)
