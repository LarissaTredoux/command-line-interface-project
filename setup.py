from setuptools import setup

setup(
    name='vtc',
    version='0.1',
    py_modules=['vtc'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        vtc=vtc6666:main
    ''',
)
