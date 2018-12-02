from distutils.core import setup

setup(name='rpq',
      version='1.0.0',
      description='request queue for reverse proxy',
      author='Volodymyr Savchenko',
      author_email='contact@volodymyrsavchenko.com',
      license='GPLv3',
      packages=['rpq'],
      zip_safe=False,

      entry_points={
          'console_scripts': [
            'rpq = rpq.service:main',
            ]
      },

      install_requires=[
      ],

      url = 'https://github.com/volodymyrss/rpq',
      download_url = 'https://github.com/volodymyrss/rpq/archive/1.0.0.tar.gz',
      keywords = [],
      classifiers = [],
     )

