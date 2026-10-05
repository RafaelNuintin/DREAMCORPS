# Mapeamento de IDs de exemplo conforme o tileset base:
# 0: Vazio / Fora do Mapa
# 1: Chão de Madeira (Phase I & V)
# 2: Parede Listrada
# 3: Chão de Azulejo Rosa (Phase II)
# 4: Chão Aquático/Azulejo Azul (Phase III)
# 5: Fragmento/Chão Distorcido (Phase IV)
# 10: Cama | 11: Mesa de Computador | 12: TV | 13: Armário | 14: Janela

# --- PHASE I: THE BEDROOM (Quarto Inicial) ---
# --- PHASE I: THE BEDROOM (Matriz 10x8) ---
LEVEL_1_BACKGROUND = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 4, 5, 2, 2, 2, 2], # Parede com janela centralizada (Tiles 4 e 5)
    [2, 2, 3, 2, 2, 2, 2, 2, 2, 2], # Relógio na parede (Tile 3)
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

LEVEL_1_OBJECTS = [
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0, 6,  7,  0, 10, 11, 13, 14, 15, 16], # Cama, Computador, TV e Guarda-roupa
    [0, 8,  9,  0,  0, 12,  0,  0, 15, 16], # Parte inferior dos móveis
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
    [0, 0,  0,  0,  0,  0,  0,  0,  0,  0],
]

# --- PHASE II: THE SCHOOL (Weirdcore School) ---
LEVEL_2_BACKGROUND = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
]

# --- PHASE III: THE OFFICE (Frutiger Aero) ---
LEVEL_3_BACKGROUND = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4],
]

# --- PHASE IV: THE NULL (Ambiente Glitch) ---
LEVEL_4_BACKGROUND = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 5, 5, 0, 0, 5, 5, 5, 0, 0],
    [0, 5, 5, 5, 0, 0, 5, 5, 0, 0],
    [0, 0, 5, 5, 5, 5, 0, 0, 0, 0],
    [0, 0, 0, 0, 5, 5, 5, 0, 0, 0],
]

# --- PHASE V: REALITY? (Quarto Modificado) ---
LEVEL_5_BACKGROUND = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [2, 2, 2, 2, 15, 2, 2, 2, 2, 2], # Tile 15 = Janela Surreal
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]