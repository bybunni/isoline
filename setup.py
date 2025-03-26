from setuptools import setup, find_packages

setup(
    name="isoline",
    version="0.1.0",
    description="Vector graphics isometric game engine built on pyglet",
    author="Isoline Team",
    packages=find_packages(),
    install_requires=[
        "pyglet>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "isoline=isoline.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
)
