from setuptools import setup, find_packages


with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='ezmaps',
    version = '1.1.0',
    description= 'Generate Beautiful Maps',
    author = 'c00kie17',
    author_email = 'anshul1708@gmail.com',
    url = 'https://github.com/c00kie17/ezmaps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'ezmaps = ezmaps.__main__:main',
        ]
    },
    install_requires=[
        'tqdm',
        'pillow',
        'requests'
    ],
)