from setuptools import setup
import re

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

with open('ipyc/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

with open('README.rst') as f:
    readme = f.read()


extras_require = {
    'docs': [
        'sphinx==3.0.3',
        'sphinxcontrib_trio==1.1.2',
        'sphinxcontrib-websupport',
    ]
}


setup(name='IPyC',
      author='dovedevic',
      url='https://github.com/dovedevic/IPyC',
      project_urls={
        "Documentation": "https://ipyc.readthedocs.io/",
        "Issue tracker": "https://github.com/dovedevic/IPyC/issues",
      },
      version=version,
      packages=['ipyc'],
      license='MIT',
      description='A basic IPC implementation for Python',
      long_description=readme,
      long_description_content_type="text/x-rst",
      install_requires=requirements,
      python_requires='>=3.5.3',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ]
)
