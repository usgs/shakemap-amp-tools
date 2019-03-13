from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize
import glob

# it is no longer necessary to point to a specific C compiler,
# since the installation of the platform specific ones set the CC
# environment variable to the appropriate executable.

setup(name='amptools',
      version='0.1dev',
      description='USGS ShakeMap Strong Motion Data Tools',
      include_package_data=True,
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['amptools'],
      scripts=glob.glob('bin/*')
      )
