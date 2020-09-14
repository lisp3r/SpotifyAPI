import setuptools

with open("README.md", "r") as fh: long_description = fh.read()

setuptools.setup(
    name="example-pkg-lisp3r",
    version="0.1",
    author="lisp3r",
    author_email="none",
    description="Spotify API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lisp3r/SpotifySmth",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
