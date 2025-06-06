from setuptools import setup, find_packages

setup(
    name="j1tools",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "lark>=1.1.5",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",  # for coverage reporting
        ],
    },
    entry_points={
        "console_scripts": [
            "j1asm=j1tools.assembler.asm:main",
            "hex2coe=j1tools.memory.memory:main",
            "hex2mif=j1tools.memory.memory:main",
            "mif2mem=j1tools.memory.memory:main",
            "rebuild_make=j1tools.utils.rebuild_make:main",
        ],
    },
    author="Brandon Blodget",
    author_email="brandon.blodget@example.com",
    description="Tools for J1 Forth CPU development",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bblodget/J1_ArtyS7_Bringup",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
