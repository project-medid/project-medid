from setuptools import setup

setup(
    name='pydiwsi',
    version='0.1',
    packages=['pydeidentlib'],
    url='https://medicine.ai.uky.edu',
    license='Apache 2.0',
    author='Cody Bumgardner',
    author_email='ai@uky.edu',
    description='Python Library for WSI Deidentification',
    install_requires=['Pillow', 'lxml', 'tinynumpy'],

)
