import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="raViz",
    version="0.1.0",
    author="Christopher Mendoza",
    author_email="camendoza7@miners.utep.edu",
    description="Package to help create flow visualizations",
    long_description='''
# Ra
Ra helps easily generate geographic visualization using the folium package.
[Github Link](https://github.com/utepnetlab/ra)

## Installation

```bash
pip install raViz
```

## Usage
```python
import ra
import pandas as pd

df = pd.read_csv('mycsv.csv')
ra = ra.Map(df)
ra.createMap()
ra.saveMap('MyMap.html')
```
## Contributing
Anyone is welcome to contribute, if you'd like send a pull request for major changes with the changes you'd like to make.

## License
[MIT](https://choosealicense.com/licenses/mit/)
''',
    long_description_content_type="text/markdown",
    url="https://github.com/utepnetlab/ra",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)