from setuptools import setup, find_packages

setup(
    name='keyguard',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'scikit-learn',
        'joblib',
        'psutil',
        'pynput',
        'bcrypt'
    ],
    entry_points={
        'console_scripts': [
            'keyguard=keyguard.cli:main',
        ],
    },
)
