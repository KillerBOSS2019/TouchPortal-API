from setuptools import setup  #, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: MacOS',
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3.9'
]

setup(
  name='TouchPortal API',
  version='1.4',
  description='Touch Portal API for Python',
  long_description=open('README.md').read(),
  long_description_content_type="text/markdown",
  url='https://github.com/KillerBOSS2019/TouchPortal-API',
  author='Damien',
  author_email='DamienWeiFen@gmail.com',
  license='MIT',
  classifiers=classifiers,
  keywords='TouchPortal, API, Plugin',
  packages=['TouchPortalAPI'],
  python_requires='>=3.8',
  install_requires=[
      'pyee',
      'requests'
      ]
)
