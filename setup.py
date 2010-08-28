from artie import VERSION
from setuptools import setup

setup(
	name='artie',
	version=VERSION,
	url='http://github.com/sumeet/artie',
	author='Sumeet Agarwal',
	author_email='sumeet.a@gmail.com',
	description='IRC utility robot framework for Python',
	packages=['artie',],
	scripts=['bin/artie-run.py',],
	install_requires=['twisted', 'pyyaml',],
	setup_requires=['setuptools_trial',],
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: No Input/Output (Daemon)',
		'Intended Audience :: Developers',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Communications :: Chat :: Internet Relay Chat',
	]
)
