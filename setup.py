import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="node-io",
    version="0.1.0",
    author="Miraculous Owonubi",
    author_email="omiraculous@gmail.com",
    description="A minor rewrite of the NodeJS Stream API for efficient stream management based on the `node_events` EventEmitter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Apache-2.0',
    url="https://github.com/miraclx/node-io",
    packages=['node-io'],
    install_requires=['node-events'],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
)
