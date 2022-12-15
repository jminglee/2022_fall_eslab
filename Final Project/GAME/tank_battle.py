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
PLAYER_SPEED = 3
ENEMY_SPEED  = 1
BULLET_SPEED = 5

class Level():
    def __init__(self, init_level=0):
        self.level  = init_level
        
    def next_level(self,player):
        self.level += 1
        self.num_enemy = 2+self.level*2//3 if self.level <= 10 else 8-(self.level-10)//2
        self.num_block = 22+self.level*3//2

        self.pos_enemy = list()
        while len(self.pos_enemy) < self.num_enemy:
            pos = (20*(random.randint(0, SCREEN_W-20)//20)+10, 20*(random.randint(40, SCREEN_H-20)//20)+10)
            while pos in self.pos_enemy or (abs(pos[0]-player.rect.centerx)<20 and abs(pos[1]-player.rect.centery)<20):
                pos = (20*(random.randint(0, SCREEN_W-20)//20)+10, 20*(random.randint(40, SCREEN_H-20)//20)+10)
            self.pos_enemy.append(pos)

        self.pos_block = list()
        while len(self.pos_block) < self.num_block:
            pos = (20*(random.randint(0, SCREEN_W-20)//20)+10, 20*(random.randint(40, SCREEN_H-20)//20)+10)
            while pos in self.pos_enemy or pos in self.pos_block or (abs(pos[0]-player.rect.centerx)<20 and abs(pos[1]-player.rect.centery)<20):
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
    def __init__(self):
        super(Player, self).__init__()
        self.max_life = 10
        self.life = 10
        self.image = pygame.Surface([20,20])
        self.image.fill(GREEN)
        self.image.set_alpha(255*self.life/self.max_life) 
        self.rect = self.image.get_rect(center=(50,50))
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

    def next_level(self):
        self.life = min(self.max_life, self.life+self.max_life//3)
        self.image.set_alpha(255*self.life/self.max_life) 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.max_life = 1
        self.life = 1
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.image.set_alpha(255*self.life/self.max_life) 
        self.rect = self.image.get_rect(center=(pos[0],pos[1]))
        self.speed = ENEMY_SPEED
        self.direction = RIGHT
        self.bullet_counter = 1

    def update(self, player:Player, blocks):
        if abs(player.rect.centerx-self.rect.centerx) >= abs(player.rect.centery-self.rect.centery):
            if player.rect.centerx > self.rect.centerx:
                if   self.check_move_r(blocks): self.move_r()
                elif player.rect.centery > self.rect.centery:
                    if   self.check_move_u(blocks): self.move_u()
                    elif self.check_move_d(blocks): self.move_d()
                elif player.rect.centery < self.rect.centery:
                    if   self.check_move_d(blocks): self.move_d()
                    elif self.check_move_u(blocks): self.move_u()
                else: self.move_r()
            elif player.rect.centerx < self.rect.centerx:
                if   self.check_move_l(blocks): self.move_l()
                elif player.rect.centery > self.rect.centery:
                    if   self.check_move_u(blocks): self.move_u()
                    elif self.check_move_d(blocks): self.move_d()
                elif player.rect.centery < self.rect.centery:
                    if   self.check_move_d(blocks): self.move_d()
                    elif self.check_move_u(blocks): self.move_u()
                else: self.move_r()
        else:
            if player.rect.centery > self.rect.centery:
                if   self.check_move_d(blocks): self.move_d()
                elif player.rect.centerx > self.rect.centerx:
                    if   self.check_move_r(blocks): self.move_r()
                    elif self.check_move_l(blocks): self.move_l()
                elif player.rect.centerx < self.rect.centerx:
                    if   self.check_move_l(blocks): self.move_l()
                    elif self.check_move_r(blocks): self.move_r()
                else: self.move_d()
            elif player.rect.centery < self.rect.centery:
                if   self.check_move_u(blocks): self.move_u()
                elif player.rect.centerx > self.rect.centerx:
                    if   self.check_move_r(blocks): self.move_r()
                    elif self.check_move_l(blocks): self.move_l()
                elif player.rect.centerx < self.rect.centerx:
                    if   self.check_move_l(blocks): self.move_l()
                    elif self.check_move_r(blocks): self.move_r()
                else: self.move_d()

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_W:
            self.rect.right = SCREEN_W
        if self.rect.top <= SCREEN_TOP:
            self.rect.top = SCREEN_TOP
        elif self.rect.bottom >= SCREEN_H:
            self.rect.bottom = SCREEN_H

        if self.bullet_counter != 0: 
            self.bullet_counter += 1
            self.bullet_counter %= 60

    def check_move_u(self, blocks): 
        enable = True
        for block in blocks:
            if abs(self.rect.centerx-block.rect.centerx) < 20 and abs((self.rect.centery-self.speed)-block.rect.centery) < 20: enable = False
        return enable

    def check_move_d(self, blocks): 
        enable = True
        for block in blocks:
            if abs(self.rect.centerx-block.rect.centerx) < 20 and abs((self.rect.centery+self.speed)-block.rect.centery) < 20: enable = False
        return enable

    def check_move_l(self, blocks): 
        enable = True
        for block in blocks:
            if abs((self.rect.centerx-self.speed)-block.rect.centerx) < 20 and abs(self.rect.centery-block.rect.centery) < 20: enable = False
        return enable

    def check_move_r(self, blocks): 
        enable = True
        for block in blocks:
            if abs((self.rect.centerx+self.speed)-block.rect.centerx) < 20 and abs(self.rect.centery-block.rect.centery) < 20: enable = False
        return enable

    def move_u(self):
        self.rect.move_ip(0,-self.speed)
        self.direction = UP

    def move_d(self):
        self.rect.move_ip(0,self.speed)
        self.direction = DOWN

    def move_l(self):
        self.rect.move_ip(-self.speed,0)
        self.direction = LEFT

    def move_r(self):
        self.rect.move_ip(self.speed,0)
        self.direction = RIGHT

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

def game(events):
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Tanks Battle')
    clock = pygame.time.Clock()
    next_level = True
    starting   = True
    running    = True
    ending     = True

    score = 0

    big_font   = pygame.font.SysFont('Verdana', 80)
    small_font = pygame.font.SysFont('Verdana', 30)

    bg_img = pygame.image.load('pngtree-camouflage-block-texture-background-image_910986.png').convert()
    bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))
    bg_img.set_alpha(100)

    level           = Level()
    player          = Player()
    enemies         = pygame.sprite.Group()
    blocks          = pygame.sprite.Group()
    player_bullets  = pygame.sprite.Group()
    enemies_bullets = pygame.sprite.Group()
    all_item        = pygame.sprite.Group()
    all_item.add(player)

    bullet_counter  = 15
    collide_counter = 0

    while starting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if events[5].is_set():
            starting = False 

        text = big_font.render(f'Tank Battle', False, (0, 0, 0))
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

        if next_level:
            blocks.empty()
            player_bullets.empty()
            enemies_bullets.empty()
            all_item.empty()
            all_item.add(player)
            player.next_level()
            level.next_level(player)
            for i in range(level.num_enemy):
                new_enemy = Enemy(level.pos_enemy[i])
                enemies.add(new_enemy)
                all_item.add(new_enemy)
            for i in range(level.num_block):
                new_block = Block(level.pos_block[i])
                blocks.add(new_block)
                all_item.add(new_block)
            next_level = False

        screen.fill(WHITE)

        if events[5].is_set() and bullet_counter == 0:
            new_bullets = Bullet([player.rect.centerx,player.rect.centery], player.direction)
            player_bullets.add(new_bullets)
            all_item.add(new_bullets)
            bullet_counter = 1
        
        if bullet_counter != 0: 
            bullet_counter += 1
            bullet_counter %= 30

        if collide_counter != 0: 
            collide_counter += 1
            collide_counter %= 30

        player.update(events,blocks)

        for enemy in enemies:
            enemy.update(player,blocks)
            if enemy.rect.colliderect(player.rect) and collide_counter == 0:
                player.hit()
                collide_counter = 1
                if player.life == 0:
                    running = False
                    
            if enemy.bullet_counter == 0:
                new_bullets = Bullet([enemy.rect.centerx,enemy.rect.centery], enemy.direction)
                enemies_bullets.add(new_bullets)
                all_item.add(new_bullets)
                enemy.bullet_counter = 1

        for bullet in player_bullets:
            for enemy in enemies:
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    enemy.hit()
                    if enemy.life == 0:
                        score += 50

            for block in blocks:
                if bullet.rect.colliderect(block.rect):
                    bullet.kill()
                    block.hit()
                    if block.life == 0:
                        score += 10

            if bullet.alive(): 
                bullet.update()

        for bullet in enemies_bullets:
            if bullet.rect.colliderect(player.rect):
                bullet.kill()
                player.hit()
                score -= 1
                if player.life == 0:
                    running = False

            for block in blocks:
                if bullet.rect.colliderect(block.rect):
                    bullet.kill()
                    block.hit()

            if bullet.alive(): 
                bullet.update()

        if enemies.__len__() == 0:
            next_level = True

        for item in all_item:
            screen.blit(item.image, item.rect)

        text = small_font.render(f'Level: {level.level}     HP: {player.life}     Score: {score}', False, (0, 0, 0))
        screen.blit(text, (50,0))   
        pygame.draw.line(screen, BLACK, (0,SCREEN_TOP-2), (SCREEN_W, SCREEN_TOP-2), 5)
        pygame.display.flip()
        clock.tick(FPS)

    while ending:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()

        if events[5].is_set():
            ending = False

        text = big_font.render(f'Game Over', False, (0, 0, 0))
        text2 = small_font.render(f'Press bottom to continue', False, (0, 0, 0))
        screen.fill(WHITE)
        screen.blit(bg_img, (0, 0))
        screen.blit(text, ((SCREEN_W-text.get_width())/2, (SCREEN_H-text.get_height())/2)) 
        screen.blit(text2, ((SCREEN_W-text2.get_width())/2, (SCREEN_H-text2.get_height())/2+100)) 
        pygame.display.flip()
        clock.tick(FPS)
