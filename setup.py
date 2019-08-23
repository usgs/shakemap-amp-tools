from distutils.core import setup
import glob

# it is no longer necessary to point to a specific C compiler,
# since the installation of the platform specific ones set the CC
# environment variable to the appropriate executable.

setup(name='amptools',
      version='0.1',
      description='USGS ShakeMap Strong Motion Data Tools',
      include_package_data=True,
      author='Mike Hearne',
      author_email='mhearne@usgs.gov',
      url='',
      packages=['amptools'],
      scripts=glob.glob('bin/*')
      )
