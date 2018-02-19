import pygame
import random
import numpy
import json
import sys

pygame.init()
WHITE, GREEN, BLUE, RED = (255, 255, 255), (0, 255, 0), (0, 0, 255), (255, 0, 0)
CELL_SIZE = 32
WIDTH = 700
PAUSE, MUTE1, MUTE2 = pygame.image.load('buttons/pause.png'), pygame.image.load('buttons/mute1.png'), pygame.image.load(
    'buttons/mute2.png')
SOUNDTRACK, PISTOL, OUTOFAMMO = 'music/soundtrack.wav', 'music/pistol2.ogg', 'music/outofammo.ogg'
MAPPNG, MAPJSON = pygame.image.load('map/map.png'), 'map/map.json'
AIM = pygame.image.load('buttons/aim1.png')
CURSOR_BIG, CURSOR_SMALL = (60, 60), (40, 40)


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
        elif -(len(main_arr[0]) * CELL_SIZE - WIDTH) > self.x > -(len(main_arr[0]) * CELL_SIZE):
            self.x -= d
            self.rep = True
        else:
            self.x += len(main_arr[0]) * CELL_SIZE
            self.rep = False
            gui.zero()

    def render(self):
        screen.blit(self.img, (self.x, self.y))
        if self.rep:
            screen.blit(self.img, (self.x + len(main_arr[0]) * CELL_SIZE, self.y))


    def zero(self):
        self.rep = False
        self.x = 0
        spawn_z(all_sprites)
        global cam_speed
        if cam_speed < 4:
            cam_speed += 0.6


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
        self.moving = 0
        self.image = pygame.image.load(
            'appear/appear_{}.png'.format(1))
        self.rect = self.image.get_rect()
        self.rect.x = (self.x - 1) * CELL_SIZE
        self.rect.y = (self.y - 1) * CELL_SIZE - 16
        self.kk = 0
        self.kk0 = 1
        self.kk2 = 0
        self.stage = -1
        self.damage = True

    def move_cam(self, d):
        self.moving -= d
        self.rect.x -= d

    def move(self):
        if self.stage == -1:
            if 0 <= (self.x - 1) * CELL_SIZE + self.moving <= 600:
                self.stage += 1
                roar = pygame.mixer.Sound('music/brains%d.wav' % (random.randint(1, 3)))
                roar.play()
                if mute.mute:
                    roar.set_volume(0)
        if self.stage == 0:
            self.kk0 += 1
            if self.kk0 == 12.0:
                self.stage += 1
                # self.y -= 1
                self.rect.y -= 16
                return
            if int(self.kk0) == 12:
                self.stage += 1
                self.rect.y -= 16
                return
            self.image = pygame.image.load(
                'appear/appear_{}.png'.format(
                    int(self.kk0)))
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
                    self.kk = (self.kk + 1) % 10 + 1
                    self.image = pygame.image.load(
                        'walk/go_{}_r.png'.format(self.kk))
                    if self.d < 0:
                        self.image = pygame.transform.flip(self.image, True, False)
                    else:
                        pass

            else:
                self.d *= -1
        elif self.stage == 2:
            self.kk2 += 1
            if self.kk2 == 10:
                all_sprites.remove(self)
                gui.erase(self)
                del self
            else:
                self.image = pygame.image.load(
                    'die/die_{}_r.png'.format(self.kk2))
                if self.d < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
                else:
                    pass

    def render(self):
        pass

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(
                event.pos) and self.stage == 1 and gun.reload:
            self.stage = 2
            roar = pygame.mixer.Sound('music/dead_sound%d.wav' % (random.randint(1, 3)))
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
        self.x, self.y = w - 60, 40
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
        self.x, self.y = w - 110, 35
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
        self.x = 20
        self.y = 40
        self.h = 50

    def render(self):

        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.health, self.h))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, 100, self.h), 3)

    def damage(self):
        if self.health - 5 >= 0:
            self.health -= 5
            if self.health == 0:
                print('game over')
                sys.exit()


class Gun:
    def __init__(self):
        self.health = 100
        self.x = 150
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


class Count:
    def __init__(self):
        self.text = '0'
        self.font = pygame.font.SysFont('monospace', 50)

    def render(self):
        x = self.font.render('Score: ' + self.text, True, WHITE)
        screen.blit(x, (w // 2, 50))

    def add(self):
        self.text = str(int(self.text) + 1)


def parse(s):
    f = json.load(open(s))
    x = f['layers'][1]['data']
    x = numpy.array(x)
    x.resize(f['layers'][1]['height'], f['layers'][1]['width'])
    return list(x)


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
    introText = ["ЗАСТАВКА", "", 'надо засунуть сюда кнопки', 'и картиночку какую-нить']

    screen.fill(BLUE)
    font = pygame.font.Font(None, 30)
    textCoord = 50
    for line in introText:
        stringRendered = font.render(line, 1, WHITE)
        introRect = stringRendered.get_rect()
        textCoord += 10
        introRect.top = textCoord
        introRect.x = 10
        textCoord += introRect.height
        screen.blit(stringRendered, introRect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
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


gui = GUI()
health = Health()
gun = Gun()

main_arr = parse(MAPJSON)
miny, maxy = find_y(main_arr)
size = w, h = WIDTH, (maxy * CELL_SIZE - miny * CELL_SIZE)
bg = Background(0, 0, MAPPNG)
counter = Count()
gui.add_element(bg)
gui.add_element(counter)
gui.add_element(health)
gui.add_element(gun)
pause = Pause()
mute = Mute()
buttons = Buttons()
buttons.add(pause)
buttons.add(mute)
pygame.mixer.init()

cam_speed = 2
frequency = 7

all_sprites = pygame.sprite.Group()
spawn_z(all_sprites)
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()

cursor = pygame.transform.scale(AIM, CURSOR_BIG)
pygame.mixer.init()
flag = False

soundtrack = pygame.mixer.Sound(SOUNDTRACK)
soundtrack.play(loops=-1)
start_screen()
soundtrack.set_volume(0.4)
while running:
    if mute.mute:
        soundtrack.set_volume(0)
    else:
        soundtrack.set_volume(0.4)
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not pause.rect.collidepoint(event.pos) and not pause.pause and not mute.rect.collidepoint(event.pos):
                if gun.reload:
                    gun.damage()
                    cursor = pygame.transform.scale(cursor, CURSOR_SMALL)
                    snd = pygame.mixer.Sound(PISTOL)
                    snd.set_volume(0.3)
                    if not mute.mute:
                        snd.play()
                else:
                    snd = pygame.mixer.Sound(OUTOFAMMO)
                    snd.set_volume(0.7)
                    if not mute.mute:
                        snd.play()
        elif event.type == pygame.MOUSEBUTTONUP:
            if not pause.rect.collidepoint(event.pos) and not pause.pause:
                cursor = pygame.transform.scale(AIM, CURSOR_BIG)
        if not pause.pause:
            gui.get_event(event)
        buttons.apply_event(event)
        flag = pygame.mouse.get_focused()
        x, y = pygame.mouse.get_pos()

    pygame.mouse.set_visible(False)
    if not pause.pause:
        gui.move_cam(cam_speed)
        gui.move()
        gui.update()
    gui.render(screen)
    all_sprites.draw(screen)
    if flag:
        c = cursor.get_rect().width
        screen.blit(cursor, (x - c // 2, y - c // 2))

    buttons.draw(screen)
    pygame.display.flip()
    clock.tick(30)
pygame.mixer.quit()
