from distutils.core import setup

setup(name='amptools',
      version='0.1dev',
      description='USGS ShakeMap Strong Motion Data Tools',
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['amptools',
                'amptools.io',
                'amptools.io.cwb',
                'amptools.io.geonet',
                'amptools.io.knet',
                'amptools.io.cosmos',],
      scripts = ['bin/amps2xml',
                 'bin/ftpfetch',
                 'bin/sm2xml'],
)
