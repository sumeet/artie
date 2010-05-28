from setuptools import setup

setup(
	name='artie',
	version='0.1',
	url='http://github.com/sumeet/artie',
	author='Sumeet Agarwal',
	author_email='sumeet.a@gmail.com',
	description='IRC utility robot framework for Python',
	packages=['artie',],
	install_requires=['twisted', 'yaml',]
)