import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()

screen_width = 1200
screen_height = 900

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EscapeFromTsushima")

"""frame rate"""
clock = pygame.time.Clock()
FPS = 60

"""diferite variabile ale jocului"""
gravity = 0.75
scroll_thresh = 400
rows = 16
columns = 150
tile_size = screen_height // rows
tile_types = 25
max_levels = 3
screen_scroll = 1
bg_scroll = 0
level = 1
start_game = False
start_intro = False

"""variabile pentru actiunile playerilor"""
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

"""adunam toate tile-urile intr-o lista"""
img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)


"""sunete si muzica din joc"""
pygame.mixer.music.load('audio/soundtrack.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.3)
shot_fx = pygame.mixer.Sound('audio/shoot.mp3')
shot_fx.set_volume(0.1)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)
enemy_fx = pygame.mixer.Sound('audio/enemy.mp3')
enemy_fx.set_volume(0.1)




"""incarcare imaginilor"""
bullet_img = pygame.image.load("img/player/0.png").convert_alpha()
wave_img = pygame.image.load("img/icons/wave.png").convert_alpha()
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
arrow_img = pygame.image.load("img/icons/Icon29.png").convert_alpha()
grenade_img_info = pygame.image.load("img/icons/grenade1.png").convert_alpha()

"""imaginile cu butoanele din joc"""
start_img = pygame.image.load("img/start.png").convert_alpha()
exit_img = pygame.image.load("img/exit.png").convert_alpha()
restart_img = pygame.image.load("img/replay.png").convert_alpha()
backround = pygame.image.load("img/backround.png").convert_alpha()

"""imaginile pentru backround"""
pine1_img = pygame.image.load("img/background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/background/sky_cloud.png").convert_alpha()


item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

"""Culoarea sau imaginile pentru backround"""
BG = (50, 50, 50)
red = (255, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
black = (0, 0, 0)
pink = (85, 65, 54)


def draw_text(text, font, text_col, x, y):
    """Textul afisat in joc"""
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


font = pygame.font.SysFont('Futura', 30)


def draw_bg():
    """Imaginile cu backround-ul, sunt facute sa se miste incet, in timp ce se misca playerul"""
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(7):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.7, screen_height - mountain_img.get_height() - 355))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.8, screen_height - pine1_img.get_height() - 185))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.9, screen_height - pine2_img.get_height() - 15))



def reset_level():
    """Functia de reset level care ne ajuta sa restartam jocul odata ce murim"""
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    data = []
    for row in range(rows):
        r = [-1] * columns
        data.append(r)

    return data

class Ninja(pygame.sprite.Sprite):
    """Constructorul main characterului si a inamicilor"""
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.velocity_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # variabile specificae pentru AI

        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 200, 10)  # cream un rectangle care sa fie recunoscuta de AI si dupa aceea sa inceapa sa traga in player
        self.idling = False
        self.idling_counter = 0

        """toate actiunile si imaginile playerului"""

        animation_types = ["idle", "run", "jump", "attack", "dead"]
        for animation in animation_types:
            temp_list = []
            if os.path.exists(f"img/{self.char_type}/{animation}"):
                num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
                for i in range(num_of_frames):
                    img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        """Functia de miscare a playerului"""
        screen_scroll = 0
        delta_x = 0
        delta_y = 0

        if moving_left:
            delta_x = -self.speed
            self.flip = True
            self.direction = -1

        if moving_right:
            delta_x = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air:
            self.velocity_y = -14
            self.jump = False
            self.in_air = True

        self.velocity_y += gravity
        if self.velocity_y > 10:
            self.velocity_y = 10

        delta_y += self.velocity_y

        for tile in world.obstacle_list:
            """verificam coliziunile in directia x"""
            if tile[1].colliderect(self. rect.x + delta_x, self.rect.y, self.width, self.height):
                delta_x = 0
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            """verificam coliziunea in directia y"""
            if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):
                if self.velocity_y < 0:
                    self.velocity_y = 0
                    delta_y = tile[1].bottom - self.rect.top
                elif self.velocity_y >= 0:
                    self.velocity_y = 0
                    self.in_air = False
                    delta_y = tile[1].top - self.rect.bottom

        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > screen_height:
            self.health = 0


        if self.char_type == 'player':
            if self.rect.left + delta_x < 0 or self. rect. right + delta_x > screen_width:
                delta_x = 0

        self.rect.x += delta_x
        self.rect.y += delta_y

        """updatam miscarea ecranului dupa pozitia playerului"""

        if self.char_type == 'player':
            if (self.rect.right > screen_width - scroll_thresh and bg_scroll < (world.level_leght * tile_size) - screen_width) \
                or (self.rect.left < scroll_thresh and bg_scroll > abs(delta_x)):
                self.rect.x -= delta_x
                screen_scroll = -delta_x

        return screen_scroll, level_complete



    def shoot(self):

        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (1.2 * self.rect.size[0] * self.direction), self.rect.centery,
                            self.direction, self.char_type)
            bullet_group.add(bullet)
            self.ammo -= 1
            self.update_action(3)
            shot_fx.play()


    def ai(self):
        """Functia care face inamicul sa se miste, sa ne vada si sa traga in player"""
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # in timp ce inamicul sta, am updatat actiunea lui de a sta
                self.idling = True
                self.idling_counter = 50

                # verifica daca AI vede playerul
            if self.vision.colliderect(player.rect):
                # nu mai fuge si trage in player
                self.update_action(0)
                self.shoot()

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # am updatat actiunea inamicului de a fugi
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 175 * self.direction,
                                          self.rect.centery)
                    # pygame.draw.rect(screen, red, self.vision)  # aici am introdus acea linie care sa vada playerul in range-ul dorit si sa traga

                    if self.move_counter > tile_size:
                        self.direction *= -1
                        self.move_counter *= - 1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        self.rect.x += screen_scroll

    def update_animation(self):
        "fiecare animatie a playerului si a inamicului"
        animation_cooldowns = {
            0: 150,  # Idle
            1: 100,  # Run
            2: 150,  # Jump
            3: 80,  # Attack
            4: 100  # Dead
        }

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldowns.get(self.action, 100):
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 4:
                self.kill()  # daugăm această linie pentru a elimina entitatea
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            if self.action != 4:
                self.update_action(4)


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []


    def process_data(self, data):
        self.level_leght = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * tile_size
                    img_rect.y = y * tile_size
                    tile_data = (img, img_rect)
                    if tile >= 0  and tile <= 8:
                        self.obstacle_list.append(tile_data)

                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * tile_size, y * tile_size)
                        water_group.add(water)

                    elif tile >= 17 and tile <= 24:#decartiuni
                        decoration = Decoration(img, x * tile_size, y * tile_size)
                        decoration_group.add(decoration)

                    elif tile == 11:
                        #playerul nostru
                        player = Ninja("player", x * tile_size, y * tile_size, 1, 6, 20, 5)
                        health_bar = HealthBar(10, 10, player.health, player.health)

                    elif tile == 12:
                        #inamicul
                        enemy = Ninja("enemy", x * tile_size, y * tile_size, 1, 2, 20, 0)
                        enemy_group.add(enemy)

                    elif tile == 13:#sageti in plus
                        item_box = ItemBox('Ammo', x * tile_size, y * tile_size)
                        item_box_group.add(item_box)

                    elif tile == 14:#grenazi in plus
                        item_box = ItemBox("Grenade", x * tile_size, y * tile_size)
                        item_box_group.add(item_box)

                    elif tile == 15:#viata in plus
                        item_box = ItemBox('Health', x * tile_size, y * tile_size)
                        item_box_group.add(item_box)
                    elif tile == 16:#urmatorul level
                        exit = Exit(img, x * tile_size, y * tile_size)
                        exit_group.add(exit)


        return player,health_bar




    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])



class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll



class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll
        if pygame.sprite.collide_rect(self, player):
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 5
            self.kill()



class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        self.health = health
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, black, (self.x - 1, self.y - 1, 202, 12))
        pygame.draw.rect(screen, red, (self.x, self.y, 200, 10))
        pygame.draw.rect(screen, green, (self.x, self.y, 200 * ratio, 10))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, shooter):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        if shooter == 'player':
            self.image = bullet_img
        else:
            self.image = wave_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):

        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > screen_width - 50:
            self.kill()

        #verificam coliziunea cu levelul(tiles-urile)
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()



        # verificam coliziunea cu inamicul
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += gravity
        delta_x = self.direction * self.speed
        delta_y = self.vel_y

        #verifical coliziunea cu lvele-ul
        for tile in world.obstacle_list:

            if tile[1].colliderect(self.rect.x + delta_x, self.rect.y, self.width, self.height):
                self.direction *= -1
                delta_x = self.direction * self.speed

            if tile[1].colliderect(self.rect.x, self.rect.y + delta_y, self.width, self.height):

                self.speed = 0

                if self.vel_y < 0:
                    self.vel_y = 0
                    delta_y = tile[1].bottom - self.rect.top

                elif self.vel_y >= 0:
                    self.vel_y = 0
                    delta_y = tile[1].top - self.rect.bottom


        if self.rect.left + delta_x < 0 or self.rect.right + delta_x > screen_width:
            self.direction *= -1
            delta_x = self.direction * self.speed

        self.rect.x += delta_x + screen_scroll
        self.rect.y += delta_y

        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.3)
            explosion_group.add(explosion)

            if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and abs(
                    self.rect.centery - player.rect.centery) < tile_size * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and abs(
                        self.rect.centery - enemy.rect.centery) < tile_size * 2:
                    enemy.health -= 100


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        explosion_speed = 4
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed + 2
        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
            pygame.draw.rect(screen, self.colour, (screen_width // 2 + self.fade_counter, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, screen_width, screen_height // 2))
            pygame.draw.rect(screen, self.colour, (0, screen_height// 2 + self.fade_counter, screen_width, screen_height))
        if self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0, 0, screen_width, 0 + self.fade_counter))
        if self.fade_counter >= screen_width:
            fade_complete = True

        return fade_complete


"""screen transition-urile"""
intro_fade = ScreenFade(1, black, 4)
death_fade = ScreenFade(2, pink, 4)

#cream butoanele
start_button = button.Button(screen_width // 2 - 120, screen_height // 2 - 10, start_img, 1)
exit_button = button.Button(screen_width // 2 - 120, screen_height // 2 + 100, exit_img, 1)
restart_button = button.Button(screen_width // 2 - 120, screen_height // 2 - 50, restart_img, 1)



enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()




#lista pentru tiles-uri


world_data = []
for row in range(rows):
    r = [-1] * columns
    world_data.append(r)


# incarcam si cream world-ul jocului si level-urile
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:
    """Main game loop"""
    clock.tick(FPS)
    if start_game == False:
        screen.fill(BG)
        screen.blit(backround,(0, 0))
        if start_button.draw(screen):
            start_game = True
            start_intro = True

        if exit_button.draw(screen):
            run = False
    else:

        draw_bg()
        world.draw()
        health_bar.draw(player.health)

        # numarul de sageti
        draw_text(f'Ammo: ', font, white, 10, 35)
        for x in range(player.ammo):
            screen.blit(arrow_img, (80 + (x * 10), 30))

        # numarul de grenade
        draw_text(f'Grenades: ', font, white, 10, 65)
        for x in range(player.grenades):
            screen.blit(grenade_img_info, (120 + (x * 15), 62))

        if player.alive:
            player.update()
            player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()


    # update-urile pentru grupuei si afisarile pe ecran
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)


        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        if player.alive:
            # shooting
            current_time = pygame.time.get_ticks()

            if shoot:
                player.shoot()
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction), player.rect.top,
                                  player.direction)
                grenade_thrown = True
                player.grenades -= 1
                grenade_group.add(grenade)
                player.update_action(3)  # 3 inseamna ATTACK
            elif player.in_air:
                player.update_action(2)  # 2 este JUMP
            elif moving_left or moving_right:
                player.update_action(1)  # 1 inseamna RUN
            else:
                player.update_action(0)  # 0 inseamna IDLE

            screen_scroll, level_complete = player.move(moving_left, moving_right)
            print(level_complete)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= max_levels:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)


        else:
            screen_scroll = 0

            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_SPACE:
                print("Space key pressed")
                shoot = True
            if event.key == pygame.K_m:
                print("M key pressed")
                grenade = True
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_m:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
