import pygame
import random
import numpy
import json
import sys

def parse(s):
    f = json.load(open(s))
    x = f['layers'][1]['data']
    x = numpy.array(x)
    x.resize(f['layers'][1]['height'], f['layers'][1]['width'])
    return list(x)

def change_map(map):
    global main_arr
    main_arr = map[1]

pygame.init()
WHITE, GREEN, BLUE, RED, DARKBLUE = (255, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 0), (39, 45, 77)
CELL_SIZE = 32
WIDTH = 700
MAP_COL = 2
PAUSE, MUTE1, MUTE2, HEALTH, PARTICLES = pygame.image.load('buttons/pausew.png'), pygame.image.load(
    'buttons/mute1w.png'), pygame.image.load(
    'buttons/mute2w.png'), pygame.image.load('img_res/health.png'), pygame.transform.scale(
    pygame.image.load('img_res/particles.png'), (64, 64))
SOUNDTRACK, PISTOL, OUTOFAMMO = 'music/soundtrack3.wav', 'music/pistol2.ogg', 'music/outofammo.ogg'
#MAPPNG, MAPJSON = pygame.image.load('map/map2.png'), 'map/map2.json'
MAPS = [[pygame.image.load('map/map{}.png'.format(str(i))), parse('map/map{}.json'.format(str(i)))] for i in range(1, MAP_COL + 1)]
AIM = pygame.image.load('img_res/aim1w.png')
MAIN_FONT = 'fonts/6551.ttf'
CURSOR_BIG, CURSOR_SMALL = (40, 40), (30, 30)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [PARTICLES]
    for scale in (8, 16, 32):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = 0.1

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-10, 10)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Background:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.rep = False

    def move_cam(self, d):
        if self.x > -(len(main_arr[0]) * CELL_SIZE - WIDTH):
            self.x -= d
        elif self.x == -(len(main_arr[0]) * CELL_SIZE - WIDTH):
            self.rep = True
            self.x -= d
            self.next_map = random.choice(MAPS)
        elif -(len(main_arr[0]) * CELL_SIZE - WIDTH) > self.x > -(len(main_arr[0]) * CELL_SIZE):
            self.x -= d
            self.rep = True
            #self.next_map = random.choice(MAPS)
        else:
            self.x += len(main_arr[0]) * CELL_SIZE
            change_map(self.next_map)
            self.img = self.next_map[0]
            self.rep = False
            gui.zero()

    def render(self):
        screen.blit(self.img, (self.x, self.y))
        if self.rep:
            screen.blit(self.next_map[0], (self.x + len(main_arr[0]) * CELL_SIZE, self.y))

    def zero(self):
        self.rep = False
        self.x = 0
        for i in all_sprites:
            if isinstance(i, Zombie):
                gui.erase(i)
                all_sprites.remove(i)
        spawn_z(all_sprites)
        global cam_speed, current_x
        if cam_speed < 4:
            cam_speed += 0.6
        gui.spawn_medkits()
        level_counter.add()
        level_counter.show()


class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render()

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

    def move_cam(self, d):
        for element in self.elements:
            move_cam = getattr(element, "move_cam", None)
            if callable(move_cam):
                element.move_cam(d)

    def move(self):
        for element in self.elements:
            move = getattr(element, "move", None)
            if callable(move):
                element.move()

    def erase(self, x):
        for i in range(len(self.elements)):
            if self.elements[i] is x:
                self.elements.pop(i)
                break

    def zero(self):
        for element in self.elements:
            zero = getattr(element, "zero", None)
            if callable(zero):
                element.zero()

    def spawn_medkits(self):
        for i in range(len(main_arr[0])):
            if random.randrange(0, 100) <= 1:
                gui.add_element(MedKit(i, find_zy(i), all_sprites))


class Buttons(pygame.sprite.Group):
    def __init__(self):
        pygame.sprite.Group.__init__(self)

    def apply_event(self, event):
        for sprite in self:
            sprite.apply_event(event)


class Zombie(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        self.x = x
        self.y = y
        self.d = random.choice([0.1, -0.1])
        self.image = pygame.image.load(
            'appear/appear_{}.png'.format(1))
        self.rect = self.image.get_rect()
        self.rect.x = (self.x - 1) * CELL_SIZE
        self.rect.y = (self.y - 1) * CELL_SIZE - 16
        self.moving = -(CELL_SIZE // 2)
        self.sprite_num = 0
        self.stage = -1
        self.damage = True

    def move_cam(self, d):
        self.moving -= d
        self.rect.x = self.x * CELL_SIZE + self.moving

    def move(self):
        if self.stage == -1:
            if 0 <= self.rect.x <= 600:
                self.stage += 1
                roar = pygame.mixer.Sound('music/brains%d.wav' % (random.randint(1, 3)))
                roar.set_volume(0.6)
                roar.play()
                if mute.mute:
                    roar.set_volume(0)
        if self.stage == 0:
            self.sprite_num += 1
            if self.sprite_num == 12:
                self.stage += 1
                self.sprite_num = 1
                self.rect.y -= 16
                return
            self.image = pygame.image.load(
                'appear/appear_{}.png'.format(self.sprite_num))
        elif self.stage == 1:
            self.d *= random.choice([1] * 99 + [-1])

            if self.x + self.d <= 0:
                self.d *= -1
                return

            if step_able(self):
                self.x += self.d

                self.rect.x = self.x * CELL_SIZE + self.moving
                if self.rect.x < 0 and self.damage:
                    health.damage()
                    self.damage = False
                if self.rect.x > 0:
                    self.damage = True

                if self.rect.x < -50:
                    all_sprites.remove(self)
                    gui.erase(self)
                    del self

                else:
                    self.sprite_num = (self.sprite_num + 1) % 10 + 1
                    self.image = pygame.image.load(
                        'walk/go_{}_r.png'.format(self.sprite_num))
                    if self.d < 0:
                        self.image = pygame.transform.flip(self.image, True, False)


            else:
                self.d *= -1
        elif self.stage == 2:
            self.sprite_num += 1
            if self.sprite_num == 10:
                all_sprites.remove(self)
                gui.erase(self)
                del self
            else:
                self.image = pygame.image.load(
                    'die/die_{}_r.png'.format(self.sprite_num))
                if self.d < 0:
                    self.image = pygame.transform.flip(self.image, True, False)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos) and self.stage == 1 and gun.reload:
            self.stage = 2
            self.sprite_num = 0
            roar = pygame.mixer.Sound('music/dead_sound%d.wav' % (random.randint(1, 3)))
            roar.set_volume(0.6)
            roar.play()
            if mute.mute:
                roar.stop()
            x, y = self.rect.topleft
            self.rect = pygame.image.load(
                'die/die_1_r.png').get_rect()
            self.rect.x = x
            self.rect.y = ((self.y + 1) * CELL_SIZE) - self.rect.height
            counter.add()


class Pause(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pause = False
        self.image = PAUSE
        self.image = pygame.transform.scale(self.image, (50, 30))
        self.x, self.y = w - 115, 47
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def apply_event(self, event):
        if ((event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) and self.rect.collidepoint(
                event.pos)) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.pause = not self.pause


class Mute(pygame.sprite.Sprite):
    d = {False: MUTE1, True: MUTE2}

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.mute = False
        self.image = self.d[self.mute]
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.x, self.y = w - 50, 43
        self.rect = self.image.get_rect(x=self.x, y=self.y)

    def apply_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos):
            self.mute = not self.mute
            self.image = self.d[self.mute]
            self.image = pygame.transform.scale(self.image, (40, 40))


class Health:
    def __init__(self):
        self.health = 100
        self.x = 10
        self.y = 40
        self.h = 50

    def render(self):

        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.health, self.h))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 100, self.h), 3)

    def damage(self):
        global running
        if self.health - 5 > 0:
            self.health -= 5
        else:
            self.health = 0
            running = False

    def heal(self):
        extra = random.choice([5, 10, 20, 25])
        self.health = min(100, self.health + extra)


class MedKit(pygame.sprite.Sprite):
    def __init__(self, x, y, gr):
        super().__init__(gr)
        self.x = x * 32
        self.y = y * 32
        self.image = HEALTH
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.moving = 0

    def render(self):
        pygame.draw.rect(screen, pygame.Color('black'), self.rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos):
            create_particles(event.pos)
            health.heal()
            all_sprites.remove(self)
            gui.erase(self)
            del self

    def move_cam(self, d):
        self.moving -= d
        self.rect.x = self.x + self.moving


class Gun:
    def __init__(self):
        self.health = 100
        self.x = 120
        self.y = 40
        self.h = 50
        self.reload = True

    def render(self):
        pygame.draw.rect(screen, BLUE if self.reload else RED,
                         (self.x, self.y, self.health, self.h))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 100, self.h), 3)

    def damage(self):
        if self.health - 20 >= 0:
            self.health -= 20
            if self.health < 20:
                self.reload = False

    def update(self):
        if self.health + 1 < 101:
            self.health += 1
        else:
            self.reload = True


class Inscription:
    def __init__(self, x=None, y=None, text='', time_limit=0, font=50):
        self.text = text
        self.font = pygame.font.Font(MAIN_FONT, 50)
        self.x = x
        self.y = y
        if time_limit == 0:
            self.islimited = False
        else:
            self.time_limit = time_limit
            self.islimited = True
            self.time_left = 0

    def render(self):
        if self.islimited:
            if self.time_left == 0:
                rendtext = ''
            else:
                rendtext = self.text
        else:
            rendtext = self.text
        d = self.font.render(rendtext, True, WHITE)
        x = self.x if self.x != None else w // 2 - d.get_rect().width // 2 + 5
        y = self.y if self.y != None else 0
        screen.blit(d, (x, y))

    def update(self):
        if self.islimited:
            self.time_left = max(0, self.time_left - 1)

    def show(self):
        if self.islimited:
            self.time_left = self.time_limit


class Counter(Inscription):
    def __init__(self, x=None, y=None, font=50, start=0, text=None, time_limit=0):
        self.cnt = start
        self.rend = text
        self.text = self.rend + str(self.cnt)
        super().__init__(x=x, y=y, text=self.text, font=font, time_limit=time_limit)

    def add(self):
        self.cnt += 1
        self.text = self.rend + str(self.cnt)


class Label:
    def __init__(self, rect, text, text_color=DARKBLUE, background_color=pygame.Color('white')):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = background_color
        self.font_color = text_color
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font(MAIN_FONT, self.rect.height - 15)
        self.rendered_text = None
        self.rendered_rect = None

    def render(self, surface):
        if self.bgcolor != -1:
            surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)


class Button(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.bgcolor = (250, 113, 36)
        self.pressed = False

    def render(self, surface):

        if not self.pressed:
            surface.fill(self.bgcolor, self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.font_color)
            self.rendered_rect = self.rendered_text.get_rect(center=self.rect.center)
        else:
            surface.fill(self.font_color, self.rect)
            self.rendered_text = self.font.render(self.text, 1, self.bgcolor)
            self.rendered_rect = self.rendered_text.get_rect(center=self.rect.center)

        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.pressed:
            self.pressed = False
            return True
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.font_color = WHITE
            if not self.rect.collidepoint(event.pos):
                self.font_color = DARKBLUE

        return False


def step_able(z):
    f0 = int(z.x + z.d) + 1 < len(main_arr[0])
    if not f0:
        return False
    f1 = main_arr[z.y + 1][int(z.x + z.d)] not in [0] and main_arr[z.y + 1][int(z.x + z.d) + 1] not in [0]
    f2 = main_arr[z.y][int(z.x + z.d)] in [0] and main_arr[z.y][int(z.x + z.d) + 1] in [0]
    f3 = main_arr[z.y - 1][int(z.x + z.d)] in [0] and main_arr[z.y - 1][int(z.x + z.d) + 1] in [0]
    return f1 and f2 and f3


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    img = pygame.image.load('img_res/start_screen2.png')
    button_play = Button((w // 2 - 100, h // 2 - 25, 200, 50), 'PLAY')
    button_highscore = Button((w // 2 - 100, h // 2 + 35, 200, 50), 'HIGHSCORE')
    button_exit = Button((w // 2 - 100, h // 2 + 95, 200, 50), 'EXIT')
    screen.blit(img, (0, 0))
    while True:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if button_play.get_event(event):
                return
            elif button_exit.get_event(event):
                terminate()
            elif button_highscore.get_event(event):
                pass
            buttons.apply_event(event)
        screen.blit(img, (0, 0))
        button_play.render(screen)
        button_highscore.render(screen)
        button_exit.render(screen)
        buttons.draw(screen)

        pygame.display.flip()
        clock.tick(30)


def game_over_screen():
    img = pygame.image.load('img_res/game_over.png')
    button_play = Button((w // 2 - 100, h // 2 - 120, 220, 50), 'PLAY AGAIN')
    button_highscore = Button((w // 2 - 100, h // 2 - 60, 220, 50), 'HIGHSCORE')
    button_exit = Button((w // 2 - 100, h // 2, 220, 50), 'EXIT')
    screen.blit(img, (0, 0))
    while True:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if button_play.get_event(event):
                return
            elif button_exit.get_event(event):
                terminate()
            elif button_highscore.get_event(event):
                pass
            buttons.apply_event(event)
        screen.blit(img, (0, 0))
        button_play.render(screen)
        button_highscore.render(screen)
        button_exit.render(screen)
        buttons.draw(screen)

        pygame.display.flip()
        clock.tick(30)


def find_zy(g):
    ans = len(main_arr[0])
    for i in range(5, len(main_arr[0])):
        if main_arr[i][g] != 0:
            ans = min(ans, i)
            return ans - 1
    return -1


def spawn_z(all_sprites):
    global frequency
    for i in range(10, len(main_arr[0]), int(frequency)):
        y = find_zy(i)
        if y is None:
            continue
        gui.add_element(Zombie(i, y, all_sprites))
    if frequency > 3:
        frequency -= 0.5


def find_y(d):
    maxy = 0
    miny = len(d)
    for i in range(len(d[0])):
        for j in range(len(d)):
            if d[j][i] != 0:
                maxy = max(maxy, j)
                miny = min(miny, j)

    return miny, maxy

cur_map = random.choice(MAPS)
main_arr = cur_map[1]
miny, maxy = find_y(main_arr)
size = w, h = WIDTH, (maxy * CELL_SIZE - miny * CELL_SIZE)
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Zombie Shooting Range')
pygame.display.set_icon(pygame.image.load('img_res/icon.png'))
clock = pygame.time.Clock()
mute = Mute()
buttons = Buttons()
buttons.add(mute)
soundtrack = pygame.mixer.Sound(SOUNDTRACK)
# Soundtrack by  Matthew Pablo http://www.matthewpablo.com/contact
soundtrack.play(loops=-1)
start_screen()
while True:

    gui = GUI()
    health = Health()
    gun = Gun()

    bg = Background(0, 0, cur_map[0])
    counter = Counter(x=None, y=43, font=50, start=0, text='Score: ')
    gui.add_element(bg)
    gui.add_element(counter)
    gui.add_element(health)
    gui.add_element(gun)
    pause = Pause()

    buttons.add(pause)
    pygame.mixer.init()

    cam_speed = 2
    frequency = 7
    current_x = 0
    level_counter = Counter(10, 100, 50, 1, 'Level ', 100)
    gui.add_element(level_counter)
    level_counter.show()

    all_sprites = pygame.sprite.Group()
    spawn_z(all_sprites)
    gui.spawn_medkits()

    screen_rect = (0, 0, WIDTH, h)
    cursor = pygame.transform.scale(AIM, CURSOR_BIG)
    pygame.mixer.init()
    flag = False
    running = True
    soundtrack.set_volume(0.4)
    while running:
        if mute.mute:
            soundtrack.set_volume(0)
        else:
            soundtrack.set_volume(0.4)
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not pause.rect.collidepoint(event.pos) and not pause.pause and not mute.rect.collidepoint(event.pos):
                    if gun.reload:
                        gun.damage()
                        cursor = pygame.transform.scale(cursor, CURSOR_SMALL)
                        snd = pygame.mixer.Sound(PISTOL)
                        snd.set_volume(0.2)
                        if not mute.mute:
                            snd.play()
                    else:
                        snd = pygame.mixer.Sound(OUTOFAMMO)
                        snd.set_volume(0.6)
                        if not mute.mute:
                            snd.play()
            elif event.type == pygame.MOUSEBUTTONUP:
                if not pause.rect.collidepoint(event.pos) and not pause.pause:
                    cursor = pygame.transform.scale(AIM, CURSOR_BIG)
            if not pause.pause:
                gui.get_event(event)
                if not health.health:
                    running = False
            buttons.apply_event(event)
            flag = pygame.mouse.get_focused()
            x, y = pygame.mouse.get_pos()

        pygame.mouse.set_visible(False)
        if not pause.pause:
            gui.move_cam(cam_speed)
            current_x += cam_speed
            gui.move()
            gui.update()
        gui.render(screen)
        buttons.draw(screen)
        all_sprites.update()
        all_sprites.draw(screen)
        if flag:
            c = cursor.get_rect().width
            screen.blit(cursor, (x - c // 2, y - c // 2))

        pygame.display.flip()
        clock.tick(30)
    pygame.mouse.set_visible(True)
    buttons.remove(pause)
    game_over_screen()
