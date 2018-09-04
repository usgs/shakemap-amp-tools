import os
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import numpy
import glob

os.environ['CC'] = 'gcc'

sourcefiles = ["pgm/oscillators.pyx", "pgm/cfuncs.c"]

ext_modules = [Extension("pgm.oscillators",
                         sourcefiles,
                         libraries=["m"],
                         include_dirs=[numpy.get_include()],
                         extra_compile_args=["-Ofast"])]

setup(name='amptools',
      version='0.1dev',
      description='USGS ShakeMap Strong Motion Data Tools',
      include_package_data=True,
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['amptools',
                'amptools.io',
                'amptools.io.cwb',
                'amptools.io.dmg',
                'amptools.io.geonet',
                'amptools.io.knet',
                'amptools.io.cosmos',
                'amptools.io.smc',
                'amptools.io.obspy',
                'amptools.io.usc',
                'pgm',
                'pgm.imt',
                'pgm.imc'],
      package_data={'amptools': glob.glob('amptools/io/*.csv') +
                    glob.glob('tests/data/*/*'),
                    'pgm': glob.glob('amptools/io/*.csv') +
                    glob.glob('tests/data/*/*')
                    },
      scripts=['bin/amps2xml',
               'bin/ftpfetch',
               'bin/sm2xml',
               'bin/fdsnfetch',
               'bin/ingvfetch'],
      cmdclass={"build_ext": build_ext},
      ext_modules=cythonize(ext_modules)
      )
