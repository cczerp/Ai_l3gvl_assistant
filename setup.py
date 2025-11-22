"""Setup script for Legal-AI Assistant."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-legal-assistant",
    version="1.0.0",
    author="Legal-AI Team",
    description="Hybrid legal-AI system with cloud and local models, RAG, and comprehensive legal data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cczerp/Ai_l3gvl_assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Legal Industry",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "legal-ai-server=src.api.main:app",
        ],
    },
)
