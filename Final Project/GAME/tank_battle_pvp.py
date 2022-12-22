import pygame
import random

SCREEN_W   = 800
SCREEN_H   = 600
SCREEN_TOP = 40

UP    = 1
DOWN  = 2
LEFT  = 3
RIGHT = 4

BLACK      = [0,0,0]
WHITE      = [255,255,255]
RED        = [255,0,0]
GREEN      = [0,255,0]
ORANGE     = [255,165,0]
BACKGROUND = [220,220,220]

FPS = 30
PLAYER_SPEED = 90.0/FPS
ENEMY_SPEED  = 30.0/FPS
BULLET_SPEED = 150.0/FPS

class Level():
    def __init__(self, player1, player2):
        self.pos_block = list()
        self.num_block = random.randint(50,100)
        while len(self.pos_block) < self.num_block:
            pos = (20*(random.randint(0, SCREEN_W-20)//20)+10, 20*(random.randint(40, SCREEN_H-20)//20)+10)
            while pos in self.pos_enemy or pos in self.pos_block \
            or (abs(pos[0]-player1.rect.centerx)<20 and abs(pos[1]-player1.rect.centery)<20) \
            or (abs(pos[0]-player2.rect.centerx)<20 and abs(pos[1]-player2.rect.centery)<20):
                pos = (20*(random.randint(0, SCREEN_W-20)//20)+10, 20*(random.randint(40, SCREEN_H-20)//20)+10)
            self.pos_block.append(pos)

class Block(pygame.sprite.Sprite):
    def __init__(self,pos):
        super(Block, self).__init__()
        self.max_life = 4
        self.life = random.randint(self.max_life//2, self.max_life)
        self.image = pygame.Surface((20,20))
        self.image.fill(BLACK)
        self.image.set_alpha(255*self.life/self.max_life)
        self.rect = self.image.get_rect(center=(pos[0],pos[1]))

    def hit(self):
        self.life -= 1
        if self.life == 0: self.kill()
        else:              self.image.set_alpha(255*self.life/self.max_life)

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,color):
        super(Player, self).__init__()
        self.max_life = 10
        self.life = self.max_life
        self.image = pygame.Surface([20,20])
        self.image.fill(color)
        self.image.set_alpha(255*self.life/self.max_life) 
        self.rect = self.image.get_rect(center=pos)
        self.speed = PLAYER_SPEED
        self.direction = None

    def update(self, events, blocks):
        enable = True
        if events[3].is_set(): self.direction = UP
        elif events[4].is_set(): self.direction = DOWN
        elif events[1].is_set(): self.direction = LEFT
        elif events[2].is_set(): self.direction = RIGHT

        if self.direction == UP:
            for block in blocks:
                if abs(self.rect.centerx-block.rect.centerx) < 20 and abs((self.rect.centery-5)-block.rect.centery) < 20: enable = False
            if enable: self.rect.move_ip(0, -self.speed)
            
        elif self.direction == DOWN:
            for block in blocks:
                if abs(self.rect.centerx-block.rect.centerx) < 20 and abs((self.rect.centery+5)-block.rect.centery) < 20: enable = False
            if enable: self.rect.move_ip(0, self.speed)
            
        elif self.direction == LEFT:
            for block in blocks:
                if abs((self.rect.centerx-5)-block.rect.centerx) < 20 and abs(self.rect.centery-block.rect.centery) < 20: enable = False
            if enable: self.rect.move_ip(-self.speed, 0)
            
        elif self.direction == RIGHT:
            for block in blocks:
                if abs((self.rect.centerx+5)-block.rect.centerx) < 20 and abs(self.rect.centery-block.rect.centery) < 20: enable = False
            if enable: self.rect.move_ip(self.speed, 0)
            
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_W:
            self.rect.right = SCREEN_W
        if self.rect.top <= SCREEN_TOP:
            self.rect.top = SCREEN_TOP
        elif self.rect.bottom >= SCREEN_H:
            self.rect.bottom = SCREEN_H

    def hit(self):
        self.life -= 1
        if self.life == 0: self.kill()
        else:              self.image.set_alpha(255*self.life/self.max_life)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super(Bullet, self).__init__()
        self.image = pygame.Surface((10,10))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(pos[0],pos[1]))
        self.direction = direction
        self.speed = BULLET_SPEED

    def update(self):
        if self.direction == LEFT:  self.rect.move_ip(-self.speed,0)
        if self.direction == RIGHT: self.rect.move_ip(self.speed,0)
        if self.direction == UP:    self.rect.move_ip(0,-self.speed)
        if self.direction == DOWN:  self.rect.move_ip(0,self.speed)

        if self.rect.left < 0:           self.kill()
        if self.rect.right > SCREEN_W:   self.kill()
        if self.rect.top <= SCREEN_TOP:  self.kill()
        if self.rect.bottom >= SCREEN_H: self.kill()

def game(events1,events2):
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Tanks Battle PVP version')
    clock = pygame.time.Clock()
    init_level = True
    starting   = True
    running    = True
    ending     = True
    winner     = 0

    big_font   = pygame.font.SysFont('Verdana', 80)
    small_font = pygame.font.SysFont('Verdana', 30)

    bg_img = pygame.image.load('pngtree-camouflage-block-texture-background-image_910986.png').convert()
    bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
    bg_img.set_alpha(100)

    player1         = Player((50,50),GREEN)
    player2         = Player((SCREEN_W-50,SCREEN_H-50),RED)
    level           = Level(player1,player2)
    blocks          = pygame.sprite.Group()
    player1_bullets = pygame.sprite.Group()
    player2_bullets = pygame.sprite.Group()
    all_item        = pygame.sprite.Group()
    all_item.add(player1)
    all_item.add(player2)

    bullet_counter1 = 15
    bullet_counter2 = 15

    while starting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if events1[5].is_set() or events2[5].is_set():
            starting = False 

        text = big_font.render(f'Tank Battle PVP Version', False, (0, 0, 0))
        text2 = small_font.render(f'Press bottom to continue', False, (0, 0, 0))
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        screen.blit(text, ((SCREEN_W-text.get_width())/2, (SCREEN_H-text.get_height())/2)) 
        screen.blit(text2, ((SCREEN_W-text2.get_width())/2, (SCREEN_H-text2.get_height())/2+100)) 
        pygame.display.flip()
        clock.tick(FPS)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if init_level:
            for i in range(level.num_block):
                new_block = Block(level.pos_block[i])
                blocks.add(new_block)
                all_item.add(new_block)
            init_level = False

        screen.fill(WHITE)

        if events1[5].is_set() and bullet_counter1 == 0 and player1.direction != None:
            new_bullets = Bullet([player1.rect.centerx,player1.rect.centery], player1.direction)
            player1_bullets.add(new_bullets)
            all_item.add(new_bullets)
            bullet_counter1 = 1
        
        if bullet_counter1 != 0: 
            bullet_counter1 += 1
            bullet_counter1 %= 30

        if events2[5].is_set() and bullet_counter2 == 0 and player2.direction != None:
            new_bullets = Bullet([player2.rect.centerx,player2.rect.centery], player2.direction)
            player2_bullets.add(new_bullets)
            all_item.add(new_bullets)
            bullet_counter2 = 1
        
        if bullet_counter2 != 0: 
            bullet_counter2 += 1
            bullet_counter2 %= 30

        player1.update(events1,blocks)
        player2.update(events2,blocks)

        for bullet in player1_bullets:
            if bullet.rect.colliderect(player2.rect):
                bullet.kill()
                player2.hit()
                if player2.life == 0:
                    winner = 1
                    running = False

            for block in blocks:
                if bullet.rect.colliderect(block.rect):
                    bullet.kill()
                    block.hit()

            if bullet.alive(): 
                bullet.update()

        for bullet in player2_bullets:
            if bullet.rect.colliderect(player1.rect):
                bullet.kill()
                player1.hit()
                if player1.life == 0:
                    winner = 2
                    running = False

            for block in blocks:
                if bullet.rect.colliderect(block.rect):
                    bullet.kill()
                    block.hit()

            if bullet.alive(): 
                bullet.update()

        for item in all_item:
            screen.blit(item.image, item.rect)

        text = small_font.render(f'P1 HP: {player1.life}     P2 HP: {player2.life}', False, (0, 0, 0))
        screen.blit(text, (50,0))   
        pygame.draw.line(screen, BLACK, (0,SCREEN_TOP-2), (SCREEN_W, SCREEN_TOP-2), 5)
        pygame.display.flip()
        clock.tick(FPS)

    while ending:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if events1[5].is_set() or events2[5].is_set():
            ending = False

        text = big_font.render(f'Player{winner} Win!!', False, (0, 0, 0))
        text2 = small_font.render(f'Press bottom to continue', False, (0, 0, 0))
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        screen.blit(text, ((SCREEN_W-text.get_width())/2, (SCREEN_H-text.get_height())/2)) 
        screen.blit(text2, ((SCREEN_W-text2.get_width())/2, (SCREEN_H-text2.get_height())/2+100)) 
        pygame.display.flip()
        clock.tick(FPS)
