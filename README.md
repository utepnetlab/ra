# Ra
Ra helps easily generate geographic visualization using the folium package.

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
