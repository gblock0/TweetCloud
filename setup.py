from setuptools import setup, find_packages

import versioneer

setup(
    name="tweetcloud",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    url="https://github.com/gblock0/TweetCloud",
    entry_points={"console_scripts": ["tweetcloud = tweetcloud.app:main"]},
    install_requires=[
        "matplotlib==3.3.*",
        "pandas==1.1.*",
        "pillow==7.2.*",
        "python-twitter==3.*",
        "wordcloud==1.7.*",
    ],
)
