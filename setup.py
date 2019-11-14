from setuptools import setup

setup(
    name='tetrapod',
    version='0.1',
    py_modules='tetrapod',
    install_requires=['Click', 'requests', 'requests_oauthlib', 'python-dateutil' ],
    entry_points='''
        [console_scripts]
        tpod=tetrapod.cli:cli
    ''',
)
