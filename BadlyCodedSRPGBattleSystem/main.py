import random

import pygame

pygame.init()
window = pygame.display.set_mode((500, 300))
clock = pygame.time.Clock()
enemy = pygame.image.load('enemy.png')
player = pygame.image.load('player.png')

colors = {'g': (40, 128, 40), 'd': (90, 60, 40)}

tilemap = [
    'ggddg',
    'gdddd',
    'gdddg',
    'gdddg',
    'gdddg',
    'gdddg'
]
entitymap = [
    ["0", "0", "0", "0", "0"],
    ["0", "o", "0", "o", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "0", "0", "0", "0"],
    ["0", "0", "p", "0", "0"],
]
columns, rows = len(tilemap[0]), len(tilemap)
isometric_size = 0
isometric_tiles = {}
for key, color in colors.items():
    tile_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    tile_surf.fill(color)
    tile_surf = pygame.transform.rotate(tile_surf, 45)
    isometric_size = tile_surf.get_width()
    tile_surf = pygame.transform.scale(tile_surf, (isometric_size, isometric_size // 2))
    isometric_tiles[key] = tile_surf
tile_size = (isometric_size, isometric_size // 2)


def tileRect(column, row, tile_size):
    x = (column + row) * tile_size[0] // 2
    y = ((columns - column - 1) + row) * tile_size[1] // 2
    return pygame.Rect(x, y, *tile_size)


game_map = pygame.Surface(((columns + rows) * isometric_size // 2, (columns + rows) * isometric_size // 4),
                          pygame.SRCALPHA)


def draw_tiles():
    global column, row, tile_surf, tile_rect
    for column in range(columns):
        for row in range(rows):
            tile_surf = isometric_tiles[tilemap[row][column]]
            tile_rect = tileRect(column, row, tile_size)
            game_map.blit(tile_surf, tile_rect)


draw_tiles()


def draw_entities():
    global column, row, tile_rect
    for column in range(columns):
        for row in range(rows):
            if entitymap[row][column] == 'o':
                tile_rect = tileRect(column, row, tile_size)
                game_map.blit(enemy, (tile_rect.x + 15, tile_rect.y))
            if entitymap[row][column] == 'p':
                tile_rect = tileRect(column, row, tile_size)
                game_map.blit(player, (tile_rect.x + 15, tile_rect.y))


draw_entities()

map_rect = game_map.get_rect(center=window.get_rect().center)
map_outline = [
    pygame.math.Vector2(0, columns * isometric_size / 4),
    pygame.math.Vector2(columns * isometric_size / 2, 0),
    pygame.math.Vector2((columns + rows) * isometric_size // 2, rows * isometric_size / 4),
    pygame.math.Vector2(rows * isometric_size / 2, (columns + rows) * isometric_size // 4)
]
for pt in map_outline:
    pt += map_rect.topleft

origin = map_outline[0]
x_axis = (map_outline[1] - map_outline[0]) / columns
y_axis = (map_outline[3] - map_outline[0]) / rows


def inverseMat2x2(m):
    a, b, c, d = m[0].x, m[0].y, m[1].x, m[1].y
    det = 1 / (a * d - b * c)
    return [(d * det, -b * det), (-c * det, a * det)]


point_to_grid = inverseMat2x2((x_axis, y_axis))


def transform(p, mat2x2):
    x = p[0] * mat2x2[0][0] + p[1] * mat2x2[1][0]
    y = p[0] * mat2x2[0][1] + p[1] * mat2x2[1][1]
    return pygame.math.Vector2(x, y)


font = pygame.font.SysFont(None, 30)
textO = font.render("O", True, (255, 255, 255))

movePlayer = False
playersTurn = True
p_col, p_row = 2, 2
SELECTED_TILE = None
OLD_SELECTED_TILE = None
run = True
while run:
    clock.tick(100)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            m_pos = pygame.mouse.get_pos()
            m_grid_pos = transform(pygame.math.Vector2(m_pos) - origin, point_to_grid)
            m_col, m_row = int(m_grid_pos[0]), int(m_grid_pos[1])

            SELECTED_TILE = (m_row, m_col)

            if movePlayer:
                possibleMoves = (
                (OLD_SELECTED_TILE[0] - 1, OLD_SELECTED_TILE[1]), (OLD_SELECTED_TILE[0] + 1, OLD_SELECTED_TILE[1]),
                (OLD_SELECTED_TILE[0], OLD_SELECTED_TILE[1] - 1), (OLD_SELECTED_TILE[0], OLD_SELECTED_TILE[1] + 1))

                if (SELECTED_TILE[0], SELECTED_TILE[1]) in possibleMoves:
                    entitymap[OLD_SELECTED_TILE[0]][OLD_SELECTED_TILE[1]] = '0'
                    entitymap[SELECTED_TILE[0]][SELECTED_TILE[1]] = 'p'
                    movePlayer = False
                    playersTurn = False

            if playersTurn and entitymap[m_row][m_col] == 'p':
                movePlayer = True
                OLD_SELECTED_TILE = SELECTED_TILE

        if event.type == pygame.MOUSEBUTTONUP and movePlayer:
            pass

    if playersTurn == False:
        for column in range(columns):
            for row in range(rows):
                if entitymap[row][column] == 'o':
                    possibleMoves = (
                        (column - 1, row),
                        (column + 1, row),
                        (column, row),
                        (column, row))

                    n = random.choice(possibleMoves)

                    if not (0 <= n[0] < len(entitymap) and 0 <= n[1] < len(entitymap[0])):
                        continue

                    entitymap[row][column] = '0'
                    entitymap[n[0]][n[1]] = 'o'
                    playersTurn = True

    p_position = transform((p_col + 0.5, p_row + 0.5), (x_axis, y_axis)) + origin
    m_pos = pygame.mouse.get_pos()
    m_grid_pos = transform(pygame.math.Vector2(m_pos) - origin, point_to_grid)
    m_col, m_row = int(m_grid_pos[0]), int(m_grid_pos[1])

    window.fill((0, 0, 0))
    draw_tiles()
    draw_entities()
    window.blit(game_map, map_rect)

    if 0 <= m_grid_pos[0] < columns and 0 <= m_grid_pos[1] < rows:
        tile_rect = tileRect(m_col, m_row, tile_size).move(map_rect.topleft)
        pts = [tile_rect.midleft, tile_rect.midtop, tile_rect.midright, tile_rect.midbottom]
        pygame.draw.lines(window, (255, 255, 255), True, pts, 4)
    pygame.display.update()

pygame.quit()
exit()