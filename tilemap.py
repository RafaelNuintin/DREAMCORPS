import pygame

TILE_SIZE = 32

class Tilemap:
    def __init__(self, tileset_image_path, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.tileset = pygame.image.load(tileset_image_path).convert_alpha()
        self.tiles = {}
        self._slice_tileset()

    def _slice_tileset(self):
        """Recorta o tileset em sub-superfícies de 32x32 mapeadas por um ID inteiro."""
        cols = self.tileset.get_width() // self.tile_size
        rows = self.tileset.get_height() // self.tile_size
        
        tile_id = 0
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    c * self.tile_size, 
                    r * self.tile_size, 
                    self.tile_size, 
                    self.tile_size
                )
                self.tiles[tile_id] = self.tileset.subsurface(rect)
                tile_id += 1

    def draw(self, surface, matrix, offset_x=0, offset_y=0):
        """Renderiza a matriz do nível na tela de acordo com o mapeamento numérico."""
        for row_idx, row in enumerate(matrix):
            for col_idx, tile_id in enumerate(row):
                if tile_id in self.tiles:
                    x = col_idx * self.tile_size + offset_x
                    y = row_idx * self.tile_size + offset_y
                    surface.blit(self.tiles[tile_id], (x, y))