from setuptools import find_packages, setup

setup(name='opfython',
      version='1.0.0',
      description='A Python-inspired Optimum-Path Forest',
      author='Recogna Laboratory',
      author_email='gth.rosa@uol.com.br',
      url='https://github.com/gugarosa/opfython',
      license='MIT',
      install_requires=['numpy>=1.13.3',
                        'pandas>=0.24.1',
                        'pylint>=1.7.4',
                        'pytest>=3.2.3',
                       ],
      extras_require={
          'tests': ['pytest',
                    'pytest-pep8',
                   ],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
