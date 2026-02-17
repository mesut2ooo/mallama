from setuptools import setup, find_packages

setup(
    name="ollama-webui",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "requests>=2.28.0",
        "werkzeug>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ollama-webui=ollama_webui.__main__:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A beautiful web interface for Ollama",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ollama-webui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)