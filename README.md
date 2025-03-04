# sentinelloader
Sentinel-2 satellite tiles images downloader from Copernicus. 

With this utility you can specify the desired polygon, image resolution, band name and aproximate dates and it will do the best effort to find all tiles needed to satisfy your requirement. Then it will download minimal data by selecting just the needed .jp2 files inside Products, combine downloaded tiles, crop the combined tiles image to the polygon and cache the results, returning a GeoTIFF image with raster for the selected area.

All API calls are in ESP:4326 reference.

# Background

Granules are packages containing data taken from Sentinel-2 satellite for a region on the globe in a specific time. They contain a lot of data for that area (13 bands in different resolutions and other derived bands and quality data). Level-2A products, for example, have ~1GB of data for a single tile (100km2 x 100km2). 

With this utility you can select which bands/resolutions to download. For example, if you need only the TCI band (true color) tile at 60m resolution, you will can use the utility to download just ~3MB of data (instead of 1GB!). For max resolution(10m), each band will have ~120MB. Some caching will be applied to avoid re-downloading of data that is already present in disk.

* For more information on Sentinel-2 satellite product data, go to https://sentinel.esa.int/documents/247904/685211/Sentinel-2-Products-Specification-Document

* If you want to download whole Granules (instead of only some files inside Granules), you can go to https://github.com/sentinelsat/sentinelsat or https://scihub.copernicus.eu/twiki/do/view/SciHubUserGuide/BatchScripting?redirectedfrom=SciHubUserGuide.8BatchScripting


## Usage

### Docker example

* Create docker-compose.yml

```yml
version: '3.3'
services:
  sentinelloader:
    image: flaviostutz/sentinelloader
    environment:
      - COPERNICUS_USER=auser
      - COPERNICUS_PASSWORD=apass
    ports:
      - 8686:8888
```

* Create an account in Copernicus and change info in docker-compose.yml accordingly

* Run ```docker-compose up -d```

* Open your browser at http://localhost:8686/

* Open Jupyter notebook "example.ipynb" and press "Run"

* You should see something like [this](/notebooks/example.ipynb)

### Python example

```shell
pip install git+https://github.com/flaviostutz/sentinelloader
```

```python
import logging
import os
from osgeo import gdal
import matplotlib.pyplot as plt
from sentinelloader import Sentinel2Loader
from shapely.geometry import Polygon

sl = SentinelLoader('/notebooks/data/output/sentinelcache', 
                    'mycopernicususername', 'mycopernicuspassword',
                    apiUrl='https://scihub.copernicus.eu/apihub/', showProgressbars=True, loglevel=logging.DEBUG)

area = Polygon([(-47.873796, -16.044801), (-47.933796, -16.044801),
        (-47.933796, -15.924801), (-47.873796, -15.924801)])

geoTiffs = sl.getRegionHistory(area, 'TCI', '60m', '2019-01-06', '2019-01-30', daysStep=5)
for geoTiff in geoTiffs:
    print('Desired image was prepared at')
    print(geoTiff)
    os.remove(geoTiff)
)
```

For a Jupyter example, [click here](notebooks/example.ipynb)
