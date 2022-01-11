from setuptools import setup  #, find_packages
from pathlib import Path
from re import search

base_path = Path(__file__).parent

repo_url = 'https://github.com/KillerBOSS2019/TouchPortal-API/'
home_url = repo_url
docs_url = 'https://KillerBOSS2019.github.io/TouchPortal-API/'
long_description = (base_path / "README.md").read_text("utf8")
api_version = search(
  r'__version__ = "(.+?)"', (base_path / "TouchPortalAPI" / "__init__.py").read_text("utf8")
).group(1)

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: MacOS',
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
  'Programming Language :: Python :: 3',
  'Programming Language :: Python :: 3.8',
  'Programming Language :: Python :: 3.9',
  'Programming Language :: Python :: 3.10'
]

setup(
  name = 'TouchPortal API',
  version = api_version,
  description = 'Touch Portal API and SDK for Python',
  long_description = long_description,
  long_description_content_type = "text/markdown",
  url = home_url,
  project_urls = {
    'Documentation': docs_url,
    'Source': repo_url,
    'Issues': repo_url + "issues",
  },
  author = 'Damien',
  author_email=  'DamienWeiFen@gmail.com',
  license = 'GPLv3+',
  classifiers = classifiers,
  keywords = 'TouchPortal, Touch Portal, API, Plugin, SDK',
  packages = ['TouchPortalAPI'],
  python_requires = '>=3.8',
  install_requires = [
    'pyee',
    'requests'
  ],
  extras_require = {
    'dev': [
      'pdoc',
    ]
  },
  entry_points = {
    'console_scripts': ['tppsdk=TouchPortalAPI.sdk_tools:main']
  }
)
