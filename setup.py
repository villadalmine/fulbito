from setuptools import setup

setup(name='fulbito',
      version='0.1',
      description='CLI futbol stats',
      url='http://github.com/villadalmine/fulbito',
      author='Restaurador',
      author_email='villadalmine@gmail.com',
      license='MIT',
      packages=['fulbito'],
      zip_safe=False,
      entry_points={
        'console_scripts': [
            'fulbito = fulbito.main:main'
        ]
      }
    )

