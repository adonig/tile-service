# tile-service

A vector tile server made with [aiohttp](https://aiohttp.readthedocs.io/en/stable/). It serves [Mapbox Vector Tiles](https://www.gdal.org/drv_mvt.html) from an MBTiles SQLite database file.

Because it is asynchronous, it can handle heavy load and does even better behind a load balancer and a cache (i.e. an AWS API Gateway).

I began adding fontstack support, but stopped working on it, when I realized it is possible to do everything serverless (cheaper and easier to maintain).

