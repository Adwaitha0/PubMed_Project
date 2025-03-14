from setuptools import setup

setup(
    name="fetch_papers", 
    version="0.1.0",  
    py_modules=["fetch_papers"], 
    install_requires=["requests", "xmltodict"],
    author="Adwaitha",
    author_email="adwaithapk2018@gmail.com",
    description="A Python module to fetch paper details from PubMed",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Adwaitha0/PubMed_Project",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
