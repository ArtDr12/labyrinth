import pygame, random
from config import *

SCREEN_SIZE = 840

class PygameFacade:
    def __init__(self, screen_size, caption='Noname'):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)

    def draw_circle(self, x, y, color, radius):
        pygame.draw.circle(self.screen, color, (x, y), radius)

    def draw_rectangle(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, pygame.Rect(x, y, width, height))

    def draw_triangle(self, x1, y1, x2, y2, x3, y3, color):
        pygame.draw.polygon(self.screen, color, ((x1, y1), (x2, y2), (x3, y3)))

    def display_text(self, text, x, y, color):
        self.screen.blit(self.font.render(text, True, color), (x, y))

    def update_screen(self):
        pygame.display.flip()

    def clear_screen(self):
        self.screen.fill(BACKGROUND_COLOR)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

class Player:
    def __init__(self, facade, x, y, grid_size):
        self.facade = facade
        self.x = x 
        self.y = y
        self.grid_size = grid_size
        self.color = PLAYER_COLOR

    def draw(self):
        self.facade.draw_circle((self.x + 0.5) * self.grid_size, (self.y + 0.5) * self.grid_size, self.color, self.grid_size // 3)

    def move_left(self): self.x -= 1 
    def move_right(self): self.x += 1 
    def move_up(self): self.y -= 1 
    def move_down(self): self.y += 1

    def check_collision(self, cell):
        if cell == 2: player.x, player.y = 0, n - 1
        if cell == 4: return True

class Trap:
    def __init__(self, facade, x, y, grid_size, move_direction):
        self.facade = facade
        self.x = x 
        self.y = y
        self.grid_size = grid_size
        self.move_direction = move_direction
        self.t = 0
        self.color = TRAP_COLOR if self.move_direction == [0, 0] else MOVING_TRAP_COLOR
        self.move_delay = TRAP_MOVE_DELAY

    def draw(self):
        self.facade.draw_rectangle(self.grid_size * self.x, self.grid_size * self.y, self.grid_size, self.grid_size, self.color)

    def move(self, n):
        if self.move_direction != (0, 0):
            self.t += 1
            if self.t == self.move_delay:
                new_x = self.x + self.move_direction[0] 
                new_y = self.y + self.move_direction[1]
                
                if not (0 <= new_x <= n-1) or not (0 <= new_y <= n-1) or a[new_x][new_y] != 0:
                    self.move_direction = [-i for i in self.move_direction]
                    new_x = self.x + self.move_direction[0]
                    new_y = self.y + self.move_direction[1]

                a[self.x][self.y] = 0
                self.t = 0 
                self.x = new_x
                self.y = new_y
                a[self.x][self.y] = 2

traps_list = []

def generateLevel(SCREEN_SIZE, k, traps, key, moving_traps, facade):
    global traps_list
    traps_list = []
    g = [[1] * k for _ in range(k)]
    st = [(random.randrange(k // 2) * 2, random.randrange(k // 2) * 2)]
    while st:
        x, y = st[-1]
        g[x][y] = 0
        n = [(x + dx, y + dy) for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)] if 0 <= x + dx < k and 0 <= y + dy < k and g[x + dx][y + dy]]
        if n:
            nx, ny = random.choice(n)
            g[(x + nx) // 2][(y + ny) // 2] = 0
            st.append((nx, ny))
        else:
            st.pop()
    g[k - 1][0] = g[0][k - 1] = 0 

    visited = [[False for _ in range(k)] for _ in range(k)]
    path = [(0, k-1)]

    def dfs(x, y):
        if x == k-1 and y == 0:
            return True
        visited[x][y] = True
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < k and 0 <= ny < k and not visited[nx][ny] and g[nx][ny] == 0:
                path.append((nx, ny))
                if dfs(nx, ny): return True
                path.pop()
        return False

    dfs(0, k-1)

    if traps:
        grid_size = SCREEN_SIZE // k

        for _ in range(random.randint(k * k // 40, k * k // 15)): 
            while True:
                x, y = random.randint(0, k - 1), random.randint(0, k - 1)
                if g[x][y] == 0 and (x, y) not in path:
                    g[x][y] = 2
                    move_direction = [[0, 0]]
                    if moving_traps:
                        if x > 0 and g[x-1][y] == 0: move_direction.append([-1, 0])
                        if x < k - 1 and g[x+1][y] == 0: move_direction.append([1, 0])
                        if y > 0 and g[x][y-1] == 0: move_direction.append([0, -1])
                        if y < k - 1 and g[x][y+1] == 0: move_direction.append([0, 1])
                    traps_list.append(Trap(facade, x, y, grid_size, random.choice(move_direction)))
                    break

    if key:
        f = False

        while not f:
            t = 0
            lock_x = lock_y = -1

            while True:
                lock_x, lock_y = random.choice(path[1:-1])
                if g[lock_x][lock_y] == 0: 
                    g[lock_x][lock_y] = 3 
                    break

            while t < KEY_PLACEMENT_LIMIT:
                x, y = random.randint(0, k - 1), random.randint(0, k - 1)
                if g[x][y] == 0 and (x, y) not in path:
                    visited_key = [[False for _ in range(k)] for _ in range(k)]
                    def dfs_to_key(cx, cy):
                        if cx == x and cy == y: return True
                        visited_key[cx][cy] = True
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < k and 0 <= ny < k and not visited_key[nx][ny] and g[nx][ny] == 0:
                                if dfs_to_key(nx, ny): return True
                        return False

                    if dfs_to_key(0, k - 1):
                        g[x][y] = 4
                        f = True
                        break
                    else:
                        t += 1 
            else:
                g[lock_x][lock_y] = 0

    return g

n = square = level = 0
levels = {1: [5, "WASD to move", "Get to the opposite corner"], 2: [7], 3: [8], 4: [10], 5: [10, "Collect the key to open the lock"], 6: [11], 7: [12], 8: [13], 9: [14], 10: [10, "Avoid the traps"], 11: [10], 12: [12], 13: [14], 14: [15], 15: [18], 16: [20], 17: [21], 18: [22], 19: [24], 20: [7, "You win"]}

pygame_facade = PygameFacade((SCREEN_SIZE, SCREEN_SIZE), "Maze")
player = Player(pygame_facade, 0, 0, 0)
start = True

running = True
while running:
    if (player.x == n-1 and player.y == 0) or start:
        level += 1
        n = levels[level][0]
        square = SCREEN_SIZE // n
        text = [f"Level {level}"] + levels[level][1:]
        a = generateLevel(SCREEN_SIZE, n, True if level > 9 else False, True if level > 4 else False, True if level > 10 else False, pygame_facade)
        player = Player(pygame_facade, 0, n-1, square)
        start = False
        if level == 15: TRAP_MOVE_DELAY *= TRAP_DELAY_MULTIPLIER

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if player.y > 0 and a[player.x][player.y-1] % 2 != 1: player.move_up()
            elif event.key == pygame.K_a:
                if player.x > 0 and a[player.x-1][player.y] % 2 != 1: player.move_left()
            elif event.key == pygame.K_s:
                if player.y < n - 1 and a[player.x][player.y+1] % 2 != 1: player.move_down()
            elif event.key == pygame.K_d:
                if player.x < n - 1 and a[player.x+1][player.y] % 2 != 1: player.move_right()

    pygame_facade.clear_screen()

    for trap in traps_list:
        trap.move(n)
        trap.draw()

    for i in range(n):
        for j in range(n):
            if a[i][j] == 1: pygame_facade.draw_rectangle(square * i, square * j, square, square, WALL_COLOR)
            elif a[i][j] == 3: pygame_facade.draw_rectangle(square * i, square * j, square, square, LOCK_COLOR)
            elif a[i][j] == 4: pygame_facade.draw_rectangle(square * i, square * j, square, square, KEY_COLOR)
    
    pygame_facade.draw_triangle(0, SCREEN_SIZE, square, SCREEN_SIZE, 0, SCREEN_SIZE - square, START_COLOR)
    pygame_facade.draw_triangle(SCREEN_SIZE, 0, SCREEN_SIZE - square, 0, SCREEN_SIZE, square, FINISH_COLOR)

    for i in range(len(text)):
        pygame_facade.display_text(text[i], 50, 50+i*48, WHITE)

    if player.check_collision(a[player.x][player.y]):
        a[player.x][player.y] = 0
        for i in range(n):
            for j in range(n):
                if a[i][j] == 3: a[i][j] = 0

    player.draw()

    pygame_facade.update_screen()
    pygame_facade.clock.tick(FPS)

pygame.quit()
