import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wdlpmt",
    version="0.0.1",
    author='Guanliang Meng',
    author_email='linzhi2012@gmail.com',
    description="A tool for mangage WDL pipeplines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3',
    url='https://github.com/linzhi2013/wdl_dep_resolution',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['poetry_semver', 'mixology', 'requests'],

    entry_points={
        'console_scripts': [
            'wdlpmt=wdlpmt.wdlpmt:get_para',
        ],
    },
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
    ),
)