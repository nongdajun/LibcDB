from setuptools import setup, find_packages

# from pkg_resources import parse_requirements

# with open("requirements.txt", encoding="utf-8") as fp:
#     install_requires = [str(requirement) for requirement in parse_requirements(fp)]

setup(
    name="LibcDB",
    version="0.1.0",
    author="NONG DaJun",
    author_email="ndj8886@163.com",
    description="pwntools extend library",
    long_description="pwntools extend library",
    license="",
    url="https://github.com/nongdajun/LibcDB",
    install_requires=[],
    data_files=[("./libc_db/data", ["./libc_db/data/libc.sqlite3"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    packages=["libc_db"]
)
