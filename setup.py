import setuptools

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setuptools.setup(
    name="logparser3",
    version="1.0.4",
    author="logpai",
    author_email="logpai@users.noreply.github.com",
    description="A machine learning toolkit for log parsing from LOGPAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/logpai/logparser",
    download_url='https://github.com/logpai/logparser/tags',
    packages=setuptools.find_packages(
        exclude=["tests", "data", "docs", "example"]),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["regex==2022.3.2", "numpy", "pandas", "scipy", "tqdm", "scikit-learn"],
    classifiers=(
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
    license="Apache-2.0 License",
    keywords=['log analysis', 'log parsing', 'AIOps']
)
