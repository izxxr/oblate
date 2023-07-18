from setuptools import setup

VERSION = "0.2.0"
GITHUB = "https://github.com/izxxr/oblate"
DOCUMENTATION = "https://oblate.readthedocs.io"
LICENSE = "MIT"
PACKAGES = ["oblate"]

with open("README.MD", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

with open("requirements.txt", "r") as f:
    REQUIREMENTS = f.readlines()

    while "\n" in REQUIREMENTS:
        REQUIREMENTS.remove("\n")

EXTRA_REQUIREMENTS = {}

setup(
    name="oblate",
    author="izxxr",
    version=VERSION,
    license=LICENSE,
    url=GITHUB,
    project_urls={
        "Documentation": DOCUMENTATION,
        "Issue tracker": GITHUB + "/issues",
    },
    description='Python library for data validation',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=REQUIREMENTS,
    extra_requires=EXTRA_REQUIREMENTS,
    packages=PACKAGES,
    python_requires='>=3.7.0',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
    ]
)