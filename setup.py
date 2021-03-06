#!/usr/bin/env python3
import os, sys, fileinput, site
from setuptools.command.install import install as installer
from setuptools import setup
from setuptools import find_packages
from subprocess import call

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

class install(installer):
	def run(self):
		installer.run(self)
		path = site.getsitepackages()[0]
		# service
		filename = '/etc/init.d/piserver'
		s = open(filename).read()
		s = s.replace('{user_local_lib_python}', path)
		f=open(filename, 'w')
		f.write(s)
		f.flush()
		f.close()
		os.chmod(filename, 0o755)
		# executable
		filename = path + '/piserver/piserver.py'
		os.chmod(filename, 0o755)
		# registeR
		call(["update-rc.d", "piserver", "remove"])
		call(["update-rc.d", "piserver", "defaults", "99"])
		call(["ln", "-s", "/usr/local/lib/python3.4/dist-packages/piserver/piserver.py", "/usr/local/bin/"])
		call(["mv", "/usr/local/bin/piserver.py", "/usr/local/bin/piserver"])
		call(["rm", "/usr/local/piserver/piserver.sq3"])
		call(["touch", "/var/log/piserver/piserver.log"])
		os.chmod("/var/log/piserver/piserver.log", 0o766)

setup(
	name='piserver',
	version='1.1',
	install_requires=["bottle>=0.12", "pycurl>=7.19", "pyalsaaudio>=0.8", "watchdog>=0.8", "picamera>=1.6"],
	description='PiServer, domotic server for RF433, Freebox, Temp & Light Sensor that expose data by web interface and api',
	long_description=read('README.md'),
	author='Benjamin Touchard',
	author_email='benjamin@kolapsis.com',
	url='http://www.kolapsis.com/',
	package_dir={'piserver': 'src'},
	packages=['piserver', 'piserver.core', 'piserver.modules'],
	include_package_data=True,
	package_data={
		'static':['src/static/*'],
		'views':['src/views/*'],
		'imgs':['src/imgs/*']
	},
	data_files=[('piserver', ['src/conf/config.json', 'src/conf/rules.json', 'src/conf/homeeasy.json', 'src/conf/alarms.json', 'src/conf/sensors.json']),
				('/etc/init.d', ['src/boot/piserver'])],
	cmdclass={'install': install},
)
