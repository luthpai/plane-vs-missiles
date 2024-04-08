import pygame, sys, yaml, random
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    QUIT,
    K_w,
    K_a,
    K_s,
    K_d,
)

pygame.mixer.init()
pygame.init()

SCREEN_WIDTH = 860
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
clock = pygame.time.Clock()

collide_sound = pygame.mixer.Sound("./assets/collide.wav")
complete_sound = pygame.mixer.Sound("./assets/complete.wav")
over_sound = pygame.mixer.Sound("./assets/over.wav")

pygame.mixer.music.load("./assets/music.mp3")
pygame.mixer.music.play(loops=-1)

fps = 90


def get_font(size):
    return pygame.font.Font("./assets/Kanit-Regular.ttf", size)


class Button:
    # This class is made by Baraltech on Github.
    # Thanks to him.
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.image = pygame.transform.scale(self.image, (160, 60))
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[
            1
        ] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.surf = pygame.image.load("./assets/plane.png")
        self.surf = pygame.transform.scale(self.surf, (90, 50))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=((100), (SCREEN_HEIGHT - self.surf.get_width()) / 2)
        )
        self.lives = 3

    def update(self, pressed):
        if pressed[K_UP] or pressed[K_w]:
            self.rect.move_ip(0, -5)
        if pressed[K_DOWN] or pressed[K_s]:
            self.rect.move_ip(0, 5)
        if pressed[K_LEFT] or pressed[K_a]:
            self.rect.move_ip(-5, 0)
        if pressed[K_RIGHT] or pressed[K_d]:
            self.rect.move_ip(5, 0)

        if pressed[K_ESCAPE]:
            self.lives = 0
            self.kill()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super(Enemy, self).__init__()
        self.surf = pygame.image.load("./assets/missile.png")
        self.surf = pygame.transform.scale(self.surf, (40, 20))
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )
        self.speed = random.randint(5, 15)

    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()


class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.surf = pygame.image.load("./assets/cloud.png")
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # self.surf.set_alpha(200)
        self.rect = self.surf.get_rect(
            center=(
                random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100),
                random.randint(0, SCREEN_HEIGHT),
            )
        )

    def update(self):
        self.rect.move_ip(-5, 0)
        if self.rect.right < 0:
            self.kill()


def play():
    pygame.display.set_caption("Plane vs Missiles")

    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 250)

    ADDCLOUD = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDCLOUD, 1000)

    player = Player()

    enemies = pygame.sprite.Group()
    clouds = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    running = True
    start = True
    collided_in_previous_frame = False

    score = 0
    with open("./.data/highscore.yml", "r") as file:
        highscore = yaml.safe_load(file)

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                pygame.quit()
            elif event.type == ADDENEMY:
                new_enemy = Enemy()
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
            elif event.type == ADDCLOUD:
                new_cloud = Cloud()
                clouds.add(new_cloud)
                all_sprites.add(new_cloud)

        score += 5

        pressed = pygame.key.get_pressed()

        player.update(pressed)

        enemies.update()

        clouds.update()

        screen.fill("#87CEEB")

        if start:
            for entity in all_sprites:
                screen.blit(entity.surf, entity.rect)

            lives_text = get_font(18).render(f"Lives : {player.lives}", True, "#004764")
            lives_text_rect = lives_text.get_rect()
            screen.blit(lives_text, (20, 5))

            score_text = get_font(18).render(f"Score : {score}", True, "#004764")
            score_text_rect = score_text.get_rect()
            screen.blit(score_text, (130, 5))

            highscore_text = get_font(18).render(
                f"High Score : {highscore['score']}", True, "#004764"
            )
            highscore_text_rect = highscore_text.get_rect()
            screen.blit(highscore_text, (280, 5))

        collide = pygame.sprite.spritecollideany(player, enemies)

        if collide and not collided_in_previous_frame:
            collide_sound.play()
            player.lives -= 1
            print(player.lives)

        collided_in_previous_frame = collide

        if player.lives == 0:
            if score < highscore["score"]:
                over_sound.play()
            else:
                complete_sound.play()
                with open("./.data/highscore.yml", "w") as file:
                    yaml.dump({"score": score}, file)
            player.kill()
            running = False

        if player.lives == 2:
            player.surf = pygame.image.load("./assets/plane-smoked.png")
            player.surf = pygame.transform.scale(player.surf, (90, 50))
        elif player.lives == 1:
            player.surf = pygame.image.load("./assets/plane-onfire.png")
            player.surf = pygame.transform.scale(player.surf, (90, 50))

        pygame.display.flip()

        clock.tick(fps)


def menu():
    pygame.display.set_caption("Plane vs Missiles : Menu")

    while True:
        screen.fill("#87CEEB")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(70).render("Plane vs Missiles", True, "#004764")
        MENU_RECT = MENU_TEXT.get_rect(center=(SCREEN_WIDTH / 2, 150))

        with open("./.data/highscore.yml", "r") as file:
            highscore = yaml.safe_load(file)

        highscore_text = get_font(20).render(
            f"High Score: {highscore['score']}", True, "#004764"
        )
        highscore_text_rect = highscore_text.get_rect(center=(SCREEN_WIDTH / 2, 200))

        info = get_font(40).render(f"Press space to play", True, "#004764")
        info_rect = info.get_rect(center=(SCREEN_WIDTH / 2, 400))

        PLAY_BUTTON = Button(
            image=pygame.image.load("./assets/rect.png"),
            pos=(SCREEN_WIDTH / 2, 250),
            text_input="PLAY",
            font=get_font(40),
            base_color="#004764",
            hovering_color="White",
        )
        QUIT_BUTTON = Button(
            image=pygame.image.load("./assets/rect.png"),
            pos=(SCREEN_WIDTH / 2, 325),
            text_input="QUIT",
            font=get_font(40),
            base_color="#004764",
            hovering_color="White",
        )

        screen.blit(MENU_TEXT, MENU_RECT)
        screen.blit(highscore_text, highscore_text_rect)
        screen.blit(info, info_rect)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play()

        pygame.display.flip()

menu()