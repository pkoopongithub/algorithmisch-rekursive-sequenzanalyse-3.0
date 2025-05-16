from setuptools import setup, find_packages

setup(
    name="ars3",
    version="1.0.0",
    description="Algorithmisch Rekursive Sequenzanalyse 3.0 – Analyse und Simulation von Transkripten mit PCFG",
    author="Dein Name",
    author_email="dein.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "sentence-transformers",
        "hdbscan",
        "scikit-learn",
        "pandas",
        "pyyaml",
        "streamlit",
        "networkx",
        "matplotlib"
    ],
    entry_points={
        'console_scripts': [
            'ars-gui = app:main',  # Voraussetzung: app.py enthält eine main()-Funktion
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
