import logging

from aiohttp import web


log = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.get(r'/fonts/{fontstack:\s+}/{range:\s+}.pbf', name='tiles')
async def handle_fonts(request):
    fontstack = request.match_info.get('fontstack')
    fontrange = request.match_info.get('range')
    mbtiles = request.app['mbtiles']
    fonts = await mbtiles.get_fonts(fontstack, fontrange)
    if fonts:
        return web.Response(body=fonts, headers={
            'Content-Disposition': 'attachment',
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/x-protobuf',
        })
    raise web.HTTPNotFound()


@routes.get(r'/tiles/{z:\d+}/{x:\d+}/{y:\d+}.pbf', name='tiles')
async def handle_tiles(request):
    z = int(request.match_info.get('z'))
    x = int(request.match_info.get('x'))
    y = int(request.match_info.get('y'))
    mbtiles = request.app['mbtiles']
    if mbtiles.minzoom <= z <= mbtiles.maxzoom:
        tile = await mbtiles.get_tile(z, x, y)
        if tile:
            return web.Response(body=tile, headers={
                'Content-Disposition': 'attachment',
                'Content-Encoding': 'gzip',
                'Content-Type': 'application/x-protobuf',
            })
    raise web.HTTPNotFound()
