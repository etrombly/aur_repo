from distutils.core import setup

setup(
    name='aur_repo',
    version='0.1.0',
    author='etrombly',
    author_email='etrombly@gmail.com',
    packages=['package'],
    scripts=['bin/aur_repo'],
    url='https://www.github.com/etrombly/aur_repo',
    license='LICENSE',
    description='Build local repo from aur packages',
    long_description=""
)