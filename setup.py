import os

from setuptools import setup, find_packages

version_file = os.path.join(
    os.path.dirname(__file__),
    "sphinxcontrib",
    "intertex",
    "version.py",
)
with open(version_file, "r") as f:
    exec(f.read())

setup(
    name="sphinxcontrib-intertex",
    version=__version__,
    packages=find_packages(),
    namespace_packages=['sphinxcontrib'],
    url="https://github.com/mossblaser/intertex",
    author="Jonathan Heathcote",
    description="Like Intersphinx, but for Sphinx-built PDF documentation.",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
    ],
    keywords="sphinx documentation pdf latex reference",
    install_requires=["sphinx", "docutils"],
)
