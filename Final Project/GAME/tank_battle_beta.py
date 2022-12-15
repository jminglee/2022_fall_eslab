import pygame

SCREEN_W  = 800
SCREEN_H = 600

UP    = 1
DOWN  = 2
LEFT  = 3
RIGHT = 4

BLOCK1 = [105,105,105]
BLOCK2 = [128,128,128]
BLOCK3 = [169,169,169]
BLOCK4 = [192,192,192]

RED    = [255,0,0]
GREEN  = [0,255,0]
ORANGE = [255,165,0]

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super(Player, self).__init__()
        self.image = pygame.Surface([20,20])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(50,50))
        self.direction = None
        self.speed = 3

    def update(self, events):
        if events[3].is_set(): self.direction = UP
        elif events[4].is_set(): self.direction = DOWN
        elif events[1].is_set(): self.direction = LEFT
        elif events[2].is_set(): self.direction = RIGHT

        if self.direction == UP: self.rect.move_ip(0, -self.speed)  
        elif self.direction == DOWN: self.rect.move_ip(0, self.speed)  
        elif self.direction == LEFT: self.rect.move_ip(-self.speed, 0)
        elif self.direction == RIGHT: self.rect.move_ip(self.speed, 0)
            
        if self.rect.left < 0:             self.rect.left = 0
        elif self.rect.right > SCREEN_W:   self.rect.right = SCREEN_W
        if self.rect.top <= 0:             self.rect.top = 0
        elif self.rect.bottom >= SCREEN_H: self.rect.bottom = SCREEN_H

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super(Bullet, self).__init__()
        self.image = pygame.Surface((10,10))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect(center=(pos[0],pos[1]))
        self.direction = direction
        self.speed = 5

    def update(self):
        if self.direction == LEFT:  self.rect.move_ip(-self.speed,0)
        if self.direction == RIGHT: self.rect.move_ip(self.speed,0)
        if self.direction == UP:    self.rect.move_ip(0,-self.speed)
        if self.direction == DOWN:  self.rect.move_ip(0,self.speed)

def game(events):
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption('Tanks Battle')
    clock = pygame.time.Clock()
    running = True

    player   = Player()
    bullets  = pygame.sprite.Group()
    all_item = pygame.sprite.Group()
    all_item.add(player)

    bullet_counter = 0

    while running:  
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
        screen.fill((255,255,255))

        if events[5].is_set() and bullet_counter == 0 and player.direction != None:
            new_bullets = Bullet([player.rect.centerx,player.rect.centery], player.direction)
            bullets.add(new_bullets)
            all_item.add(new_bullets)
            bullet_counter = 1
        
        if bullet_counter != 0: 
            bullet_counter += 1
            bullet_counter %= 30

        player.update(events)

        for bullet in bullets:
            bullet.update()

        for item in all_item:
            screen.blit(item.image, item.rect)

        pygame.display.flip()
        clock.tick(30)
