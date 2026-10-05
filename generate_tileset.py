import os
from PIL import Image

TILE_SIZE = 32
SOURCE_IMAGE_PATH = "referencia_fase1.png"
OUTPUT_PATH = "assets/tileset.png"

def create_tileset():
    if not os.path.exists(SOURCE_IMAGE_PATH):
        print(f"Erro: '{SOURCE_IMAGE_PATH}' não encontrada na pasta do script!")
        return

    img = Image.open(SOURCE_IMAGE_PATH).convert("RGBA")
    src_w, src_h = img.size

    # Define regiões de corte em (X1, Y1, X2, Y2) proporcionais
    # Cadastramos cada peça de 32x32 individualmente
    crop_regions = [
        # --- LINHA 0: ESTRUTURA BÁSICA DA SALA ---
        None,                                                                   # ID 0: Vazio / Transparente
        (int(src_w * 0.40), int(src_h * 0.70), int(src_w * 0.50), int(src_h * 0.80)), # ID 1: Chão de Madeira (Puro)
        (int(src_w * 0.15), int(src_h * 0.12), int(src_w * 0.25), int(src_h * 0.22)), # ID 2: Parede Listrada Azul (Puro)
        (int(src_w * 0.15), int(src_h * 0.28), int(src_w * 0.25), int(src_h * 0.33)), # ID 3: Rodapé da Parede

        # --- LINHA 1: OBJETOS DE PAREDE ---
        (int(src_w * 0.08), int(src_h * 0.08), int(src_w * 0.18), int(src_h * 0.24)), # ID 4: Relógio de Parede
        (int(src_w * 0.30), int(src_h * 0.05), int(src_w * 0.43), int(src_h * 0.30)), # ID 5: Janela Topo Esq (Cortina/Lua)
        (int(src_w * 0.43), int(src_h * 0.05), int(src_w * 0.56), int(src_h * 0.30)), # ID 6: Janela Topo Dir
        (int(src_w * 0.30), int(src_h * 0.18), int(src_w * 0.43), int(src_h * 0.31)), # ID 7: Janela Base Esq

        # --- LINHA 2: CAMA (4 PEÇAS: 2x2 TILES) ---
        (int(src_w * 0.03), int(src_h * 0.35), int(src_w * 0.14), int(src_h * 0.53)), # ID 8: Cama (Topo Esq - Cabeceira)
        (int(src_w * 0.14), int(src_h * 0.35), int(src_w * 0.25), int(src_h * 0.53)), # ID 9: Cama (Topo Dir - Travesseiro)
        (int(src_w * 0.03), int(src_h * 0.53), int(src_w * 0.14), int(src_h * 0.75)), # ID 10: Cama (Pé Esq)
        (int(src_w * 0.14), int(src_h * 0.53), int(src_w * 0.25), int(src_h * 0.75)), # ID 11: Cama (Pé Dir)

        # --- LINHA 3: COMPUTADOR & ESCRIVANINHA ---
        (int(src_w * 0.28), int(src_h * 0.30), int(src_w * 0.40), int(src_h * 0.48)), # ID 12: Monitor CRT
        (int(src_w * 0.40), int(src_h * 0.30), int(src_w * 0.52), int(src_h * 0.48)), # ID 13: Teclado/Mesa
        (int(src_w * 0.38), int(src_h * 0.50), int(src_w * 0.48), int(src_h * 0.68)), # ID 14: Cadeira da Escrivaninha
        (int(src_w * 0.28), int(src_h * 0.48), int(src_w * 0.40), int(src_h * 0.65)), # ID 15: Gaveteiro da Mesa

        # --- LINHA 4: TV & GUARDA-ROUPA ---
        (int(src_w * 0.55), int(src_h * 0.32), int(src_w * 0.73), int(src_h * 0.48)), # ID 16: TV CRT (Topo)
        (int(src_w * 0.55), int(src_h * 0.48), int(src_w * 0.73), int(src_h * 0.62)), # ID 17: Hack da TV (Base)
        (int(src_w * 0.75), int(src_h * 0.22), int(src_w * 0.86), int(src_h * 0.40)), # ID 18: Guarda-Roupa (Topo)
        (int(src_w * 0.75), int(src_h * 0.40), int(src_w * 0.86), int(src_h * 0.57)), # ID 19: Guarda-Roupa (Base)
    ]

    # Cria folha de tileset 4x5 colunas/linhas
    grid_cols = 4
    grid_rows = (len(crop_regions) + grid_cols - 1) // grid_cols
    tileset_img = Image.new("RGBA", (grid_cols * TILE_SIZE, grid_rows * TILE_SIZE), (0, 0, 0, 0))

    for idx, region in enumerate(crop_regions):
        if region is None:
            continue

        cropped_tile = img.crop(region)
        # Redimensiona mantendo proporção de Pixel Art nitidamente
        resized_tile = cropped_tile.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.NEAREST)

        col = idx % grid_cols
        row = idx // grid_cols
        tileset_img.paste(resized_tile, (col * TILE_SIZE, row * TILE_SIZE))

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    tileset_img.save(OUTPUT_PATH, "PNG")
    print(f"Tileset atualizado e corrigido salvo em '{OUTPUT_PATH}'!")

if __name__ == "__main__":
    create_tileset()