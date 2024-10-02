# Define the setup function for pip installation
setup(
    name="rcaide_sai",  # This is the name used when doing `pip install rcaide_sai`
    version="1.0.0",  # Specify the version directly
    description="RCAIDE: Research Community Aerospace Interdisciplinary Design Environment",
    long_description="RCAIDE: Research Community Aerospace Interdisciplinary Design Environment",  # Short description here
    author="RCAIDE Trust",
    maintainer="The Developers",
    url="https://github.com/ssankalp26/RCAIDE",  # URL to your GitHub repo
    packages=find_packages(),  # Include RCAIDE and its sub-packages
    include_package_data=True,  # Include non-Python files (e.g., README, LICENSE)
    install_requires=[  # Define the dependencies here
        "numpy",
        "scipy",
        "scikit-learn",
        "plotly",
        "matplotlib",
        "kaleido",
        "pandas",
        "geopy",
        "importlib_metadata",
    ],
    python_requires=">=3.6",  # Minimum required Python version
    classifiers=[  # Metadata for the PyPI project
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,  # Do not zip the package
)