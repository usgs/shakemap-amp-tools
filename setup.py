from distutils.core import setup

setup(name='amptools',
      version='0.1dev',
      description='USGS ShakeMap Strong Motion Data Tools',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['amptools'],
      scripts = ['bin/amps2xml'],
)
