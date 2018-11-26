import logging
import zlib

import aiosqlite


DEFAULT_MINZOOM = 0
DEFAULT_MAXZOOM = 21


log = logging.getLogger(__name__)


class MBTiles:

    def __init__(self, path):
        self.path = path
        self.metadata = {}

    @property
    def minzoom(self):
        return int(self.metadata.get('minzoom', DEFAULT_MINZOOM))

    @property
    def maxzoom(self):
        return int(self.metadata.get('maxzoom', DEFAULT_MAXZOOM))

    @property
    def mask_level(self):
        return int(self.metadata.get('mask_level', self.maxzoom))

    async def init(self, app):
        async with aiosqlite.connect(self.path) as conn:
            async with conn.execute('SELECT name, value FROM metadata') as cursor:
                async for name, value in cursor:
                    self.metadata[name] = value

    async def get_fonts(self, fontstack, fontrange):
        async with aiosqlite.connect(self.path) as conn:
            fonts = await self._get_font(fontstack, fontrange, conn)
        if fonts:
            return fonts
        fontnames = fontstack.split(',')
        if len(fontnames) > 1:
            fonts = []
            for fontname in fontnames:
                fonts.append(await self._get_font(fontname, fontrange, conn))
            # TODO: Merge fonts, some might be None
            return fonts
        return None

    async def _get_font(self, fontstack, fontrange, conn):
        query = ('SELECT font_data'
                 '  FROM fonts'
                 ' WHERE fontstack=?'
                 '   AND range=?')
        params = [fontstack, fontrange]
        async with conn.execute(query, params) as cursor:
            async for row in cursor:
                return row[0]
        return None

    async def get_tile(self, z, x, y):
        y = (1 << z) - y - 1
        async with aiosqlite.connect(self.path) as conn:
            return await self._get_tile(z, x, y, conn)

    async def _get_tile(self, z, x, y, conn):
        query = ('SELECT tile_data'
                 '  FROM tiles'
                 ' WHERE zoom_level=?'
                 '   AND tile_column=?'
                 '   AND tile_row=?')
        params = [z, x, y]
        async with conn.execute(query, params) as cursor:
            async for row in cursor:
                return row[0]
        if z > self.mask_level:
            return await self._get_tile(z - 1, x // 2, y // 2, conn)
        return None

    def __str__(self):
        return (f'{self.__class__.__name__}('
                f'minzoom: {self.minzoom}, '
                f'maxzoom: {self.maxzoom}, '
                f'mask_level: {self.mask_level})')
