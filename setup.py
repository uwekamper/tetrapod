from setuptools import setup

setup(
    name='tetrapod',
    version='0.1',
    py_modules='tetrapod',
    install_requires=['Click', 'requests', 'requests-oauthlib', 'python-dateutil>=2' ],
    entry_points='''
        [console_scripts]
        tpod=tetrapod.cli:cli
    ''',
)
