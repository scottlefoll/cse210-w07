import pygame
from pygame import mixer
import os
import time
import random
pygame.font.init()

# set up contants:

# set up game window:
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SpaceWar")

# Load images
RED_SPACE_VESSEL = pygame.image.load("spacewar/assets/pixel_vessel_red_small2.png")
GREEN_SPACE_VESSEL = pygame.image.load("spacewar/assets/pixel_vessel_yellow_small2.png")
BLUE_SPACE_VESSEL = pygame.image.load("spacewar/assets/pixel_vessel_blue_small2.png")
# YELLOW2_SPACE_vessel = pygame.image.load("spacewar/assets/pixel_vessel_yellow_small2.png")

# Player player
YELLOW_SPACE_VESSEL = pygame.image.load("spacewar/assets/pixel_vessel_grey.png")

# beams
RED_BEAM = pygame.image.load("spacewar/assets/pixel_beam_red.png")
GREEN_BEAM = pygame.image.load("spacewar/assets/pixel_beam_green.png")
BLUE_BEAM = pygame.image.load("spacewar/assets/pixel_beam_blue.png")
YELLOW_BEAM = pygame.image.load("spacewar/assets/pixel_beam_yellow.png")

#set up the music track
SPACE_MUSIC = "spacewar/assets/starsong.mp3"

# Background
BG = pygame.transform.scale(pygame.image.load("spacewar/assets/background-star.png"), (WIDTH, HEIGHT))

class Beam:
    """A visible, moving thing that participates in the game. The result of a vessel firing.
    It has a position, a velocity, an image, and a color.
    The responsibility of beam is to move itself, draw itself, and collisions and off_screen movement. It tracks its position
    and velocity in 2d space.

    Attributes:
        x(int): the position along the x axis.
        y(int): the position along the y axis.
        img(file): the image file that displays.
        mask(pygame 2D bitmask object): tracks collisions.
    """

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Vessel:
    """A visible, moving space vehicle that participates in the game.
    It has a position, a velocity, an image, and a color.
    The responsibility of beam is to draw itself, shoot, track a "cooldown" period, 
    move its beams after firing them, and provide its own width and height.and collisions and off_screen movement. It tracks its position
    and velocity in 2d space.

    Attributes:
        x(int): the position along the x axis.
        y(int): the position along the y axis.
        vessel_img(file): the image file that displays for the vessel.
        beam_img(file): the image file that displays for the beam.
        beams(list): a list of beams that are currently active.
        cool_down_counter(int): the number of frames that the vessel has been cooling down.
    """

    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.vessel_img = None
        self.beam_img = None
        self.beams = []
        self.cool_down_counter = 0



    def draw(self, window):
        window.blit(self.vessel_img, (self.x, self.y))
        for beam in self.beams:
            beam.draw(window)



    def move_beams(self, vel, obj):
        self.cooldown()
        for beam in self.beams:
            beam.move(vel)
            if beam.off_screen(HEIGHT):
                self.beams.remove(beam)
            elif beam.collision(obj):
                obj.health -= 10
                self.beams.remove(beam)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0: 
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            beam = Beam(self.x, self.y, self.beam_img)
            self.beams.append(beam)
            self.cool_down_counter = 1

    def get_width(self):
        return self.vessel_img.get_width()

    def get_height(self):
        return self.vessel_img.get_height()
    

class Earthling(Vessel):
    """A visible, moving space vehicle from Earth that participates in the game.
    It has a position, a velocity, an image, and a color.
    The responsibility of beam is to draw itself, move its beams, 
    move its beams after firing them, and track its own health.

    Attributes:
        vessel_img(file): the image file that displays for the vessel.
        beam_img(file): the image file that displays for the beam.
        mask(pygame 2D bitmask object): tracks collisions.
        max_health(int): the maximum health of the vessel.
    """

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.vessel_img = YELLOW_SPACE_VESSEL
        self.beam_img = YELLOW_BEAM
        self.mask = pygame.mask.from_surface(self.vessel_img)
        self.max_health = health

    def move_beams(self, vel, objs):
        self.cooldown()
        for beam in self.beams:
            beam.move(vel)
            if beam.off_screen(HEIGHT):
                self.beams.remove(beam)
            else:
                for obj in objs:
                    if beam.collision(obj):
                        objs.remove(obj)
                        if beam in self.beams:
                            self.beams.remove(beam)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.vessel_img.get_height() + 10, self.vessel_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.vessel_img.get_height() + 10, self.vessel_img.get_width() * (self.health/self.max_health), 10))

class Alien(Vessel):
    """A visible, moving Alien space vehicle that participates in the game.
    It has a position, a velocity, and an image.
    The responsibility of beam is to move itself, and fire its beams.

    Attributes:
        vessel_img(file): the image file that displays for the vessel.
        beam_img(file): the image file that displays for the beam.
        mask(pygame 2D bitmask object): tracks collisions.
    """

    COLOR_MAP = {
        "red": (RED_SPACE_VESSEL, RED_BEAM),
        "green": (GREEN_SPACE_VESSEL, GREEN_BEAM),
        "blue": (BLUE_SPACE_VESSEL, BLUE_BEAM)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.vessel_img, self.beam_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.vessel_img)
    
    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            beam = Beam(self.x-20, self.y, self.beam_img)
            self.beams.append(beam)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    """An update action that handles interactions between the vessels and the beams.
    
    The responsibility of collide() is to handle the situation when the beam collides
    with the vessel.

    Arguments:
        obj1(Vessel): the first vessel.
        obj2(Beam): the beam.
        
    Returns:
        bool: True if the beam collides with the vessel, False otherwise. 
        (if the mask objects overlap, then the beam collides with the vessel)
    """

    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("sansserif", 50)
    lost_font = pygame.font.SysFont("sansserif", 60)

    aliens = []
    wave_length = 5
    alien_vel = 1

    earthling_vel = 5
    beam_vel = 5

    earthling = Earthling(300, 630)

    clock = pygame.time.Clock()

    #has to be in .mp3 format
    #has to be in same folder

    pygame.mixer.init()
    #load the music
    pygame.mixer.music.load(SPACE_MUSIC)
    # Setting the volume.
    mixer.music.set_volume(0.7)
    #play the music infinite
    pygame.mixer.music.play(-1)

    lost = False
    lost_count = 0

    # reload game graphics
    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for alien in aliens:
            alien.draw(WIN)
        
        earthling.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    # mainloop
    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or earthling.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(aliens) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                alien = Alien(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "green", "blue"]))
                aliens.append(alien)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and earthling.x - earthling_vel > 0: # left
            earthling.x -= earthling_vel
        if keys[pygame.K_RIGHT] and earthling.x + earthling_vel + earthling.get_width() < WIDTH: # right
            earthling.x += earthling_vel
        if keys[pygame.K_UP] and earthling.y - earthling_vel > 0: # up
            earthling.y -= earthling_vel
        if keys[pygame.K_DOWN] and earthling.y + earthling_vel + earthling.get_height() + 15 < HEIGHT: # down
            earthling.y += earthling_vel
        if keys[pygame.K_SPACE]:
            earthling.shoot()

        for alien in aliens[:]:
            alien.move(alien_vel)
            alien.move_beams(beam_vel, earthling)

            if random.randrange(0, 2*60) == 1:
                alien.shoot()

            if collide(alien, earthling):
                earthling.health -= 10
                aliens.remove(alien)
            elif alien.y + alien.get_height() > HEIGHT:
                lives -= 1
                aliens.remove(alien)

        earthling.move_beams(-beam_vel, aliens)

# set up the game and menu
def main_menu():
    title_font = pygame.font.SysFont("sansserif", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("WDD 230 Earthlings rule! Click the mouse to start...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

if __name__ == "__main__":
    main_menu()
