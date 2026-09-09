from setuptools import find_packages, setup

setup(
    name="tftanalyzer",
    version="0.1.0",
    description="Read-only programmatic interface to Teamfight Tactics data: Riot API client and live screen-state reader.",
    packages=find_packages(exclude=("tests", "tests.*", "examples", "tools")),
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31",
        "python-dotenv>=1.0",
        "mss>=9.0",
        "opencv-python-headless>=4.9",
        "pytesseract>=0.3.10",
        "numpy>=1.26",
        "Pillow>=10.0",
    ],
)
