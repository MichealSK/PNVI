import pygame
import random
import sys
from pygame.locals import *

pygame.init()

WIDTH, HEIGHT = 800, 600 # Висина и широчина на прозорецот
BLACK, WHITE = (0, 0, 0), (255, 255, 255) # Бои за позадината и текстот
FPS = 60 # Фрејмови по секунда

PLAYER_MOVEMENT_SPEED = 5 # Брзина со која се движи вселенскиот брод на играчот

START_METEOR_SPAWN_TIME_MIN = 1000 # Долна граница за време (во милисекунди) во кое може да се појави метеор
START_METEOR_SPAWN_TIME_MAX = 4000 # Горна граница за време (во милисекунди) во кое може да се појави метеор
START_CRYSTAL_SPEED = 4 # Брзината на кристалите на почеток на играта
START_METEOR_SPEED = 7 # Брзина на метеорите на почеток на играта
START_METEOR_SIZE_MAX = 0.3 # Почетна варијација во големината на метеорите на почеток на играта

CRYSTAL_SPAWN_SPEED = 2000 # Интервалот (во милисекунди) со која се појавуваат кристалите
CRYSTAL_SPEED_INCREASE_RATE = 1.1 # Вредоста за која се зголемува брзината на кристалите на секои 7 секунди
METEOR_SPEED_INCREASE_RATE = 1.1 # Вредоста за која се зголемува брзината на метеорите на секои 4 секунди
METEOR_SIZE_INCREASE_RATE = 0.1 # Вредноста за која се зголемува горната граница во варијацијата за големина на метеорите на секои 10 секунди
METEOR_SPAWN_TIME_INCREASE_RATE = 100 # Вредноста за која се намалуваат горната и долната граница на интервалот во кој се појавуваат метеори
MINIMUM_METEOR_SPAWN_INTERVAL = 200 # Минималната вредност која можат да ја достигнат горната и долната граница на интервалот во кој се појавуваат метеори

player_sprite = pygame.image.load("spaceship.png")
player_sprite = pygame.transform.scale(player_sprite, (
    int(player_sprite.get_width() * 0.25),
    int(player_sprite.get_height() * 0.25)
))

crystal_sprite = pygame.image.load("energy_crystal.png")
crystal_sprite = pygame.transform.scale(crystal_sprite, (
    int(crystal_sprite.get_width() * 0.025),
    int(crystal_sprite.get_height() * 0.025)
))
crystal_sprite = pygame.transform.rotozoom(crystal_sprite, 0, 1.5)

meteor_sprite = pygame.image.load("asteroid.png")
meteor_sprite = pygame.transform.scale(meteor_sprite, (
    int(meteor_sprite.get_width()),
    int(meteor_sprite.get_height())
))
meteor_sprite = pygame.transform.rotate(meteor_sprite, 0)

pygame.mixer.music.load("background_music.wav")
clash_sound = pygame.mixer.Sound("clash_sound.wav")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Scavenger!")

clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_sprite
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.collide_rect = self.rect.inflate(-20, -20)

    def update(self, keys):
        # Го поместува спрајтот и collision боксот на играчот зависно од притиснатите стрелки
        dx, dy = 0, 0
        if keys[K_LEFT] or keys[K_a]:
            dx -= PLAYER_MOVEMENT_SPEED
        if keys[K_RIGHT] or keys[K_d]:
            dx += PLAYER_MOVEMENT_SPEED
        if keys[K_UP] or keys[K_w]:
            dy -= PLAYER_MOVEMENT_SPEED
        if keys[K_DOWN] or keys[K_s]:
            dy += PLAYER_MOVEMENT_SPEED
        self.rect.x += dx
        self.rect.y += dy
        self.collide_rect.topleft = self.rect.topleft

        # Ја ограничува местоположбата на играчот во рамките на прозорецот
        self.rect.clamp_ip(screen.get_rect())
        self.collide_rect.clamp_ip(screen.get_rect())

class Crystal(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = crystal_sprite
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        max_height = max(0, HEIGHT - self.rect.height)
        self.rect.y = random.randint(0, max_height)
        self.speed = speed

    def update(self):
        # Ги придвижува кристалите на десно
        self.rect.x -= self.speed
        if self.rect.right < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, speed, size_multiplier):
        super().__init__()
        self.image = pygame.transform.rotozoom(meteor_sprite, 0, size_multiplier)
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = random.randint(0, HEIGHT - self.rect.height)
        self.collide_rect = self.rect.inflate(-40, -40)
        self.speed = speed

    def update(self):
        # Ги придвижува метеорите на десно
        self.rect.x -= self.speed
        self.collide_rect.topleft = self.rect.topleft
        if self.rect.right < 0:
            self.kill()

# Создава подгрупи на објектите кои ќе можеме да ги искористиме при детекција на допир помеѓу играчот и кристал/метеор
player = Player()
player_group = pygame.sprite.GroupSingle(player)
crystal_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

score = 0
game_over = False
font = pygame.font.Font(None, 36)

meteor_spawn_min = START_METEOR_SPAWN_TIME_MIN
meteor_spawn_max = START_METEOR_SPAWN_TIME_MAX
last_crystal_spawn = pygame.time.get_ticks()
last_meteor_spawn = pygame.time.get_ticks()

crystal_speed = START_CRYSTAL_SPEED
meteor_speed = START_METEOR_SPEED

crystal_speed_increase_time = pygame.time.get_ticks()
meteor_speed_increase_time = pygame.time.get_ticks()

meteor_size_max = START_METEOR_SIZE_MAX
size_increase_time = pygame.time.get_ticks()

pygame.mixer.music.play(loops=-1)

while True:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == KEYDOWN:
            game_over = False
            score = 0
            player.rect.center = (WIDTH // 2, HEIGHT // 2)
            crystal_group.empty()
            meteor_group.empty()
            crystal_speed = START_CRYSTAL_SPEED
            meteor_speed = START_METEOR_SPEED
            meteor_spawn_min = START_METEOR_SPAWN_TIME_MIN
            meteor_spawn_max = START_METEOR_SPAWN_TIME_MAX
            meteor_size_max = START_METEOR_SIZE_MAX
            pygame.mixer.music.play(loops=-1)

    keys = pygame.key.get_pressed()

    if not game_over:
        player_group.update(keys)
        crystal_group.update()
        meteor_group.update()

        if pygame.time.get_ticks() - last_crystal_spawn > CRYSTAL_SPAWN_SPEED:
            crystal_group.add(Crystal(crystal_speed))
            last_crystal_spawn = pygame.time.get_ticks()

        crystals_collected = [crystal for crystal in crystal_group if player.collide_rect.colliderect(crystal.rect)]
        if crystals_collected:
            score += len(crystals_collected)
            for crystal in crystals_collected:
                crystal.kill()
            clash_sound.play()

        if pygame.time.get_ticks() - last_meteor_spawn > random.randint(meteor_spawn_min, meteor_spawn_max):
            meteor_group.add(Meteor(meteor_speed, random.uniform(0.25, meteor_size_max)))
            last_meteor_spawn = pygame.time.get_ticks()

        meteors_hit = [meteor for meteor in meteor_group if player.collide_rect.colliderect(meteor.rect)]
        if meteors_hit:
            game_over = True
            pygame.mixer.music.stop()
            clash_sound.set_volume(0.8)
            clash_sound.play()

        if pygame.time.get_ticks() - crystal_speed_increase_time > 7000:
            crystal_speed *= CRYSTAL_SPEED_INCREASE_RATE
            crystal_speed_increase_time = pygame.time.get_ticks()
        if pygame.time.get_ticks() - meteor_speed_increase_time > 4000:
            meteor_speed *= METEOR_SPEED_INCREASE_RATE
            meteor_speed_increase_time = pygame.time.get_ticks()
        if pygame.time.get_ticks() - size_increase_time > 10000:
            meteor_size_max += METEOR_SIZE_INCREASE_RATE
            size_increase_time = pygame.time.get_ticks()
        if pygame.time.get_ticks() - size_increase_time > 10000:
            meteor_spawn_min = max(MINIMUM_METEOR_SPAWN_INTERVAL, meteor_spawn_min - METEOR_SPAWN_TIME_INCREASE_RATE)
            meteor_spawn_max = max(MINIMUM_METEOR_SPAWN_INTERVAL, meteor_spawn_max - METEOR_SPAWN_TIME_INCREASE_RATE)

    player_group.draw(screen)
    crystal_group.draw(screen)
    meteor_group.draw(screen)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    if game_over:
        game_over_text = font.render("GAME OVER", True, WHITE)
        text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, text_rect)

    pygame.display.flip()
    clock.tick(FPS)
