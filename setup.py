"""setup exp2 package"""

from pathlib import Path
from setuptools import find_packages, setup

HERE = Path(__file__).parent.resolve()
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="exp2",
    version="1.0",
    description="Explosion explorer",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
)
