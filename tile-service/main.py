import logging
import os
import zlib

from aiohttp import web
import aiohttp_cors
import asyncio
import click

from .routes import routes
from .mbtiles import MBTiles


ACCESS_LOG_FORMAT = '%a %t %D "%r" %s %b "%{Referer}i" "%{User-Agent}i"'


log = logging.getLogger(__name__)


async def init(loop, mbtiles):
    app = web.Application(loop=loop)

    # Initialize the tilesources.
    app['tilesources'] = [MBTiles(path=mbtiles)]
    for tilesource in app['tilesources']:
        await tilesource.init(app)
        app.on_cleanup.append(tilesource.close)
        log.debug(f'Initialized tilesource {tilesource}.')

    # Setup CORS.
    app.add_routes(routes)
    cors = aiohttp_cors.setup(app, defaults={
        '*': aiohttp_cors.ResourceOptions(
            allow_headers='*',
            expose_headers='*',
        ),
    })
    for route in app.router.routes():
        cors.add(route)

    return app


@click.command()
@click.option('--mbtiles', envvar='MBTILES', default='/data/planet.mbtiles',
              type=click.Path(exists=True), help='MBTiles file')
@click.option('--bind', '-b', envvar='BIND', default='0.0.0.0',
              help='Bind address')
@click.option('--port', '-p', envvar='PORT', default=8080, help='Port number')
def main(mbtiles, bind, port):
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop, mbtiles))
    web.run_app(app, host=bind, port=port, access_log_format=ACCESS_LOG_FORMAT)


if __name__ == '__main__':
    main()  # pylint: disable=E1120
