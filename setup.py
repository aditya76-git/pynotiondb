import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynotiondb",
    version="0.1.0",
    author="aditya76-git",
    author_email="cdr.aditya.76@gmail.com",
    description="A Python wrapper for interacting with Notion databases using SQL-style syntax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aditya76-git/pynotiondb",
    project_urls={
        "Tracker": "https://github.com/aditya76-git/pynotiondb/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.0.0",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
)