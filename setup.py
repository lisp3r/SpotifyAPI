import setuptools

with open("README.md", "r") as fh: long_description = fh.read()

setuptools.setup(
    name="spotifyapi",
    version="0.1",
    author="lisp3r",
    author_email="none",
    description="Spotify API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lisp3r/SpotifyAPI",
    packages=["spotifyapi"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    include_package_data=True,
)
