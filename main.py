import pygame
from pygame.locals import *
import math
import random
import world
import enemy
import wave

#self-made dependency to simplify vector math
import vector

pygame.init()
pygame.mixer.init()

pygame.display.set_caption("bang bang game")

WIDTH = 400
HEIGHT = 300

window = pygame.display.set_mode((WIDTH,HEIGHT))
screen = pygame.display.get_surface()

#boolean value that tracks if the program has been terminated
finish = False

#limit FPS to 60
clock = pygame.time.Clock()

gameState = "menu"

#player movement statistics
#-------------------------
moveSpeed = 4
turnSpeed = 2
speed_multiplyer = 1
#-------------------------

#player survival statistics
#-------------------------
health = 20
money = 0
Difficulty = 0
Class = 'soldier'

defense_multiplyer = 1
#-------------------------

#tracks the first frame when a player enters a shop so that they can move away from it without
#constantly being forced into the shop menu
shop = False

#tracks which slot to apply new weapons to (primary or secondary?)
selection = False

defense_upgrades = 0
speed_upgrades = 0


#initialize player weapons
#-------------------------
class Weapon():
    def __init__(self,nam,fireR,dmg,penet,typ,strnds):
        self.name = nam
        #how fast the weapon can attack (attacks/sec)
        self.fireRate = fireR
        #how much health is taken for every bullet that hits
        self.damage = dmg
        #how many objects a bullet can hit before it stops
        self.penetration = penet
        #type of attack that the weapon is (melee,gun)
        self.type = typ
        #how many rounds the player starts with if they equip this weapon
        self.startingRounds = strnds

pistol = Weapon("pistol",5,5,4,"gun",240)
machineGun = Weapon("machineGun",15,4,3,"gun",240)
rifle = Weapon("rifle",0.75,20,10,"gun",48)
fist = Weapon("fist",3,20,3,"melee",0)

primary_weapon = pistol
secondary_weapon = fist

selected_weapon = primary_weapon

bullets = selected_weapon.startingRounds
fire_timer = 0
#-------------------------

#define the view that the player has
player = world.Camera(3,3.5,-1,0,0,.66)

data = [[4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,7,7,7,7,7,7,7,7],
        [4,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
        [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
        [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
        [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
        [4,0,0,0,0,0,0,5,5,5,5,5,5,5,5,5,7,7,0,7,7,7,7,7],
        [4,0,0,0,0,0,0,5,0,5,0,5,0,5,0,5,7,0,0,0,7,7,7,1],
        [4,3,2,0,0,2,3,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,1],
        [4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,1],
        [4,0,0,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,1],
        [4,0,0,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,7,7,7,1],
        [4,0,0,0,0,0,0,5,5,5,5,0,5,5,5,5,7,7,7,7,7,7,7,1],
        [6,6,6,6,6,6,6,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
        [6,0,0,0,0,0,0,0,0,6,6,0,0,0,0,0,0,0,0,0,0,0,0,4],
        [6,6,6,6,6,6,0,6,6,6,6,0,6,6,6,6,6,6,6,6,0,0,0,6],
        [4,4,4,4,4,4,0,4,4,4,6,0,6,2,2,2,2,2,2,2,0,0,0,3],
        [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
        [4,0,0,0,0,0,0,0,0,0,0,0,6,2,0,0,5,0,0,2,0,0,0,2],
        [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
        [4,0,6,0,6,0,0,0,0,4,6,0,0,0,0,0,5,0,0,0,0,0,0,2],
        [4,0,0,5,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
        [4,0,6,0,6,0,0,0,0,4,6,0,6,2,0,0,5,0,0,2,0,0,0,2],
        [4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
        [4,4,4,4,4,4,4,4,4,4,1,1,1,2,2,2,2,2,2,3,3,3,3,3]]


level = world.World(data,[world.Entity(2,11,3),
                          world.Entity(4,4,0),
                          world.Entity(12,3,1),
                          world.Entity(18,3,1),
                          world.Entity(3,18,2)])

def roman_numeral(x):
    if x == 1:
        return 'I'
    elif x == 2:
        return 'II'
    elif x == 3:
        return 'III'
    elif x == 4:
        return 'IV'
    elif x == 5:
        return 'V'
    elif x == 6:
        return 'VI'
    elif x == 7:
        return 'VII'

#initialize wave spawning
#-------------------------
waves = [wave.Wave([0,0,0,0,0],2),
         wave.Wave([0,0,0,0,0,0,0,0],0.2),
         wave.Wave([2,0,0,0,2,0,0,0,2,0,0],0.4),
         wave.Wave([1,0,1,0,1,0,1,0,1,0,1],1),
         wave.Wave([1,1,1,1,1,1,1,1],0.5),
         wave.Wave([1,1,0,1,1,0,0,2,2,0,0,1,1,2],1),
         wave.Wave([3],1)
         ]
wave_num = 0
#-------------------------

font = pygame.font.Font(None, 36)
halfFont = pygame.font.Font(None, 18)

index = 0
timer = 0

#add all images for the play game state to the textures array
textures = []
textures.append(pygame.image.load("images/weapon/fist1.png"))
textures.append(pygame.image.load("images/weapon/fist2.png"))
textures.append(pygame.image.load("images/weapon/fist3.png"))
textures.append(pygame.image.load("images/weapon/pistol1.png"))
textures.append(pygame.image.load("images/weapon/pistol2.png"))
textures.append(pygame.image.load("images/weapon/pistol3.png"))
textures.append(pygame.image.load("images/weapon/pistol4.png"))
textures.append(pygame.image.load("images/weapon/rifle1.png"))
textures.append(pygame.image.load("images/weapon/rifle2.png"))
textures.append(pygame.image.load("images/weapon/rifle3.png"))
textures.append(pygame.image.load("images/weapon/rifle4.png"))
textures.append(pygame.image.load("images/weapon/rifle5.png"))
textures.append(pygame.image.load("images/weapon/machine_gun1.png"))
textures.append(pygame.image.load("images/weapon/machine_gun2.png"))
textures.append(pygame.image.load("images/ui/overlay.png"))
textures.append(pygame.image.load("images/ui/hpoverlay.png"))
textures.append(pygame.image.load("images/ui/hp.png"))

menu = []
menu.append(pygame.image.load("images/menu/pause/pause.png"))
menu.append(pygame.image.load("images/menu/pause/continue.png"))
menu.append(pygame.image.load("images/menu/pause/quit.png"))
menu.append(pygame.image.load("images/menu/lose.png"))
menu.append(pygame.image.load("images/menu/win.png"))
menu.append(pygame.image.load("images/menu/main/menu.png"))
menu.append(pygame.image.load("images/menu/main/easy.png"))
menu.append(pygame.image.load("images/menu/main/medium.png"))
menu.append(pygame.image.load("images/menu/main/hard.png"))
menu.append(pygame.image.load("images/menu/main/soldier.png"))
menu.append(pygame.image.load("images/menu/main/scout.png"))
menu.append(pygame.image.load("images/menu/main/heavy.png"))
menu.append(pygame.image.load("images/menu/main/selection.png"))
menu.append(pygame.image.load("images/menu/main/play.png"))
menu.append(pygame.image.load("images/menu/shop/shop.png"))
menu.append(pygame.image.load("images/menu/shop/pistol.png"))
menu.append(pygame.image.load("images/menu/shop/rifle.png"))
menu.append(pygame.image.load("images/menu/shop/machineGun.png"))
menu.append(pygame.image.load("images/menu/shop/defenseUpgrade.png"))
menu.append(pygame.image.load("images/menu/shop/speedUpgrade.png"))
menu.append(pygame.image.load("images/menu/shop/bullets1.png"))
menu.append(pygame.image.load("images/menu/shop/bullets2.png"))
menu.append(pygame.image.load("images/menu/shop/selection.png"))
menu.append(pygame.image.load("images/menu/shop/selection2.png"))


fist_animation = []
fist_animation.append([textures[0],4])
fist_animation.append([textures[2],4])
fist_animation.append([textures[1],4])

pistol_animation = []
pistol_animation.append([textures[3],2])
pistol_animation.append([textures[6],2])
pistol_animation.append([textures[5],2])
pistol_animation.append([textures[4],2])

rifle_animation = []
rifle_animation.append([textures[7],5])
rifle_animation.append([textures[8],5])
rifle_animation.append([textures[7],10])
rifle_animation.append([textures[9],5])
rifle_animation.append([textures[10],5])
rifle_animation.append([textures[11],5])
rifle_animation.append([textures[10],5])
rifle_animation.append([textures[9],5])
rifle_animation.append([textures[7],5])

machine_gun_animation = []
machine_gun_animation.append([textures[12],2])
machine_gun_animation.append([textures[13],2])

if selected_weapon.name == "fist":
    current_animation = fist_animation

if selected_weapon.name == "pistol":
    current_animation = pistol_animation

if selected_weapon.name == "rifle":
    current_animation = rifle_animation

if selected_weapon.name == "machineGun":
    current_animation = machine_gun_animation

#the index and timer will never reach > 120, so this stops the animation from playing
timer = 120
index = 120

dmg_timer = 0
trans_timer = 5

while finish != True:

    dt = clock.tick(60) * 0.001
    fps = int(clock.get_fps())

    if gameState == "menu":
        #70x40
        
        #define the rectangles that can be pressed
        easy = menu[6].get_rect()
        easy = pygame.Rect(112,106,easy.width,easy.height)

        medium = menu[7].get_rect()
        medium = pygame.Rect(202,106,medium.width,medium.height)
        
        hard = menu[8].get_rect()
        hard = pygame.Rect(292,106,hard.width,hard.height)

        soldier = menu[9].get_rect()
        soldier = pygame.Rect(112,158,soldier.width,soldier.height)

        scout = menu[10].get_rect()
        scout = pygame.Rect(202,158,scout.width,scout.height)
        
        heavy = menu[11].get_rect()
        heavy = pygame.Rect(292,158,heavy.width,heavy.height)

        play = menu[13].get_rect()
        play = pygame.Rect(250,230,play.width,play.height)
           
        
        #draw the background
        screen.blit(menu[5],screen.get_rect())
        
        if easy.collidepoint(pygame.mouse.get_pos()):
            easyTex = pygame.transform.scale(menu[6],(80,50))
            screen.blit(easyTex,(107,101))
        else:
            screen.blit(menu[6],(112,106))
            
        if Difficulty == 0:
            screen.blit(menu[12],(107,101))
            

        if  medium.collidepoint(pygame.mouse.get_pos()):
            mediumTex = pygame.transform.scale(menu[7],(80,50))
            screen.blit(mediumTex,(197,101))
        else:
            screen.blit(menu[7],(202,106))

        if Difficulty == 1:
            screen.blit(menu[12],(197,101))
            

        if  hard.collidepoint(pygame.mouse.get_pos()):
            hardTex = pygame.transform.scale(menu[8],(80,50))
            screen.blit(hardTex,(287,101))
        else:
            screen.blit(menu[8],(292,106))

        if Difficulty == 2:
            screen.blit(menu[12],(287,101))
            

        if  soldier.collidepoint(pygame.mouse.get_pos()):
            soldierTex = pygame.transform.scale(menu[9],(80,50))
            screen.blit(soldierTex,(107,151))
        else:
            screen.blit(menu[9],(112,158))

        if Class == 'soldier':
            screen.blit(menu[12],(107,151))
            

        if  scout.collidepoint(pygame.mouse.get_pos()):
            scoutTex = pygame.transform.scale(menu[10],(80,50))
            screen.blit(scoutTex,(197,151))
        else:
            screen.blit(menu[10],(202,158))

        if Class == 'scout':
            screen.blit(menu[12],(197,151))
            

        if  heavy.collidepoint(pygame.mouse.get_pos()):
            heavyTex = pygame.transform.scale(menu[11],(80,50))
            screen.blit(heavyTex,(287,151))
        else:
            screen.blit(menu[11],(292,158))

        if Class == 'heavy':
            screen.blit(menu[12],(287,151))

        if play.collidepoint(pygame.mouse.get_pos()):
            playTex = pygame.transform.scale(menu[13],(149,69))
            screen.blit(playTex,(245,225))
        else:
            screen.blit(menu[13],(250,230))
            

        events = pygame.event.get()

        for event in events:
            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True
            #resolve mouse input
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                #define the actions that each rectangle causes        
                if easy.collidepoint(pygame.mouse.get_pos()):
                    Difficulty = 0
                    
                if medium.collidepoint(pygame.mouse.get_pos()):
                    Difficulty = 1

                if hard.collidepoint(pygame.mouse.get_pos()):
                    Difficulty = 2

                if soldier.collidepoint(pygame.mouse.get_pos()):
                    Class = 'soldier'
                    
                if heavy.collidepoint(pygame.mouse.get_pos()):
                    Class = 'heavy'

                if scout.collidepoint(pygame.mouse.get_pos()):
                    Class = 'scout'

                if play.collidepoint(pygame.mouse.get_pos()):
            
                    gameState = "game"

                    if Class == "soldier":
                        speed_multiplyer = 1
                        defense_multiplyer = 1
                        
                        primary_weapon = rifle
                        secondary_weapon = pistol

                    if Class == "scout":
                        speed_multiplyer = 1.25
                        defense_multiplyer = 0.75

                        primary_weapon = rifle
                        secondary_weapon = fist

                    if Class == "heavy":
                        speed_multiplyer = 0.8
                        defense_multiplyer = 1.3

                        primary_weapon = machineGun
                        secondary_weapon = fist

                    moveSpeed = 4
                    turnSpeed = 2

                    health = 20
                    money = 0

                    defense_upgrades = 0
                    speed_upgrades = 0

                    level.entities = [world.Entity(2,11,3),
                              world.Entity(4,4,0),
                              world.Entity(12,3,1),
                              world.Entity(18,3,1),
                              world.Entity(3,18,2)]
                    
                    selected_weapon = primary_weapon

                    if selected_weapon.name == "fist":
                        current_animation = fist_animation

                    if selected_weapon.name == "pistol":
                        current_animation = pistol_animation

                    if selected_weapon.name == "rifle":
                        current_animation = rifle_animation

                    if selected_weapon.name == "machineGun":
                        current_animation = machine_gun_animation
                    
                    bullets = selected_weapon.startingRounds
                    
                    fire_timer = 0
                    
                    player = world.Camera(3,3.5,-1,0,0,.66)
                    
                    timer = 120
                    index = 120

                    dmg_timer = 0
                    trans_timer = 5

                    if Difficulty == 0:

                        waves = [wave.Wave([0,0,0],2),
                        wave.Wave([0,0,0,0,0],0.2),
                        wave.Wave([2,0,0,0,0,2,0,0],0.4),
                        wave.Wave([1,0,0,1,0,0,0,0,0,0,0,1],1),
                        wave.Wave([1,1,1,1,1],0.5),
                        wave.Wave([1,0,1,1,0,0,2,2,0,1,2],1),
                        wave.Wave([1,0,2,1,2,0,2,1],1)
                        ]
                        
                    if Difficulty == 1:

                        waves = [wave.Wave([0,0,0,0,0],2),
                        wave.Wave([0,0,0,0,0,0,0,0],0.2),
                        wave.Wave([2,0,0,0,2,0,0,0,2,0,0],0.4),
                        wave.Wave([1,0,1,0,1,0,1,0,1,0,1],1),
                        wave.Wave([1,1,1,1,1,1,1,1],0.5),
                        wave.Wave([1,1,0,1,1,0,0,2,2,0,0,1,1,2],1),
                        wave.Wave([3],1)
                        ]
                        
                    if Difficulty == 2:

                        waves = [wave.Wave([0,0,0,0,0,0,0],1),
                        wave.Wave([0,0,0,0,1,0,0,0,0,0,0],0.2),
                        wave.Wave([2,0,2,0,2,0,2,0,2,0,2],0.4),
                        wave.Wave([1,0,1,0,1,0,1,2,1,2,1],1),
                        wave.Wave([1,1,1,1,1,1,1,1,1,1,1],0.25),
                        wave.Wave([1,1,0,1,1,0,0,2,2,0,0,1,1,2],0.3),
                        wave.Wave([3,3],5)
                        ]

                    wave_num = 0

    if gameState == "shop":
        #draw the background
        screen.blit(menu[14],screen.get_rect())

        #draw all numbers that can change
        text_image = halfFont.render(str(money), True, (255,255,255))
        text_rect = text_image.get_rect(centerx=58,centery=283)
        screen.blit(text_image, text_rect)

        text_image = halfFont.render(str(speed_upgrades), True, (255,255,255))
        text_rect = text_image.get_rect(centerx=117,centery=283)
        screen.blit(text_image, text_rect)

        text_image = halfFont.render(str(defense_upgrades), True, (255,255,255))
        text_rect = text_image.get_rect(centerx=172,centery=283)
        screen.blit(text_image, text_rect)

        text_image = halfFont.render(str(bullets), True, (255,255,255))
        text_rect = text_image.get_rect(centerx=224,centery=283)
        screen.blit(text_image, text_rect)

        #define all the rectangles that can be pressed

        #subtract 8 from the height to prevent overlapping
        pist = menu[15].get_rect()
        pist = pygame.Rect(35,106,pist.width,pist.height - 8)

        if pist.collidepoint(pygame.mouse.get_pos()):
            pistolTex = pygame.transform.scale(menu[15],(65,65))
            screen.blit(pistolTex,(35,101))
        else:
            screen.blit(menu[15],(40,106))

        rif = menu[16].get_rect()
        rif = pygame.Rect(35,156,rif.width,rif.height - 8)

        if rif.collidepoint(pygame.mouse.get_pos()):
            rifleTex = pygame.transform.scale(menu[16],(65,65))
            screen.blit(rifleTex,(35,151))
        else:
            screen.blit(menu[16],(40,156))

        mg = menu[17].get_rect()
        mg = pygame.Rect(35,206,mg.width,mg.height - 8)

        if mg.collidepoint(pygame.mouse.get_pos()):
            mgTex = pygame.transform.scale(menu[17],(65,65))
            screen.blit(mgTex,(35,201))
        else:
            screen.blit(menu[17],(40,206))

        defense = menu[18].get_rect()
        defense = pygame.Rect(165,106,defense.width,defense.height)

        if defense.collidepoint(pygame.mouse.get_pos()):
            defenseTex = pygame.transform.scale(menu[18],(65,65))
            screen.blit(defenseTex,(165,101))
        else:
            screen.blit(menu[18],(170,106))

        speed = menu[19].get_rect()
        speed = pygame.Rect(165,186,speed.width,speed.height)

        if speed.collidepoint(pygame.mouse.get_pos()):
            speedTex = pygame.transform.scale(menu[19],(65,65))
            screen.blit(speedTex,(165,181))
        else:
            screen.blit(menu[19],(170,186))

        smlbullets = menu[20].get_rect()
        smlbullets = pygame.Rect(285,106,defense.width,defense.height)

        if smlbullets.collidepoint(pygame.mouse.get_pos()):
            smlbulletsTex = pygame.transform.scale(menu[20],(65,65))
            screen.blit(smlbulletsTex,(280,101))
        else:
            screen.blit(menu[20],(285,106))

        lrgbullets = menu[21].get_rect()
        lrgbullets = pygame.Rect(285,186,lrgbullets.width,lrgbullets.height)

        if lrgbullets.collidepoint(pygame.mouse.get_pos()):
            lrgbulletsTex = pygame.transform.scale(menu[21],(65,65))
            screen.blit(lrgbulletsTex,(280,181))
        else:
            screen.blit(menu[21],(285,186))

        if selection:
            slotRawTex = menu[23]
        else:
            slotRawTex = menu[22]

        slot = slotRawTex.get_rect()        
        slot = pygame.Rect(10,10,slot.width,slot.height)

        if slot.collidepoint(pygame.mouse.get_pos()):
            slotTex = pygame.transform.scale(slotRawTex,(60,60))
            screen.blit(slotTex,(5,5))
        else:
            slotTex = pygame.transform.scale(slotRawTex,(50,50))
            screen.blit(slotTex,(10,10))

        events = pygame.event.get()

        for event in events:
            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True
            
            #quit if the player presses escape
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                gameState = "game"

            #resolve mouse input
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
                #define the actions that each rectangle causes
                if pist.collidepoint(pygame.mouse.get_pos()):
                    if money >= 12:
                        money -= 12
                        if selection:
                            secondary_weapon = pistol
                        else:
                            primary_weapon = pistol

                if rif.collidepoint(pygame.mouse.get_pos()):
                    if money >= 24:
                        money -= 24
                        if selection:
                            secondary_weapon = rifle
                        else:
                            primary_weapon = rifle
                    
                if mg.collidepoint(pygame.mouse.get_pos()):
                    if money >= 48:
                        money -= 48
                        if selection:
                            secondary_weapon = machineGun
                        else:
                            primary_weapon = machineGun

                if defense.collidepoint(pygame.mouse.get_pos()):
                    if money >= 50 and defense_upgrades < 10:
                        money -= 50
                        defense_upgrades += 1

                if speed.collidepoint(pygame.mouse.get_pos()):
                    if money >= 50 and speed_upgrades < 10:
                        money -= 50
                        speed_upgrades += 1

                if smlbullets.collidepoint(pygame.mouse.get_pos()):
                    if money >= 50:
                        money -= 50
                        bullets += 32

                if lrgbullets.collidepoint(pygame.mouse.get_pos()):
                    if money >= 80:
                        money -= 80
                        bullets += 64

                if slot.collidepoint(pygame.mouse.get_pos()):
                    selection = not selection

        selected_weapon = primary_weapon

    if gameState == "win":
        #draw the background
        screen.blit(menu[4],screen.get_rect())
        #80, 190, 300;;; 200
        text_image = font.render(str(int(health)) + '/20', True, (255,255,255))
        text_rect = text_image.get_rect(centerx=80,centery=200)
        screen.blit(text_image, text_rect)
        
        text_image = font.render(str(money), True, (255,255,255))
        text_rect = text_image.get_rect(centerx=190,centery=200)
        screen.blit(text_image, text_rect)

        text_image = font.render('easy', True, (255,255,255))
        text_rect = text_image.get_rect(centerx=300,centery=200)
        screen.blit(text_image, text_rect)
        
        events = pygame.event.get()

        for event in events:
            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True
            #resolve mouse input
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                gameState = "menu"

    if gameState == "death":
        #draw the background
        screen.blit(menu[3],screen.get_rect())

        events = pygame.event.get()

        for event in events:
            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True
            #resolve mouse input
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                gameState = "menu"
    
    if gameState == "pause":

        #draw the current level to the screen
        level.draw(player.pos[0],player.pos[1],player.dir[0],player.dir[1]
                   ,player.plane[0],player.plane[1],screen)

        #draw the pause menu in front of the level overlay
        screen.blit(menu[0],screen.get_rect())
        
        screen.blit(menu[1],(90,150))
        screen.blit(menu[2],(200,150))

        events = pygame.event.get()

        for event in events:
            #quit if the player presses escape
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                gameState = "game"

            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True

            #resolve mouse input
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
                #define the rectangles that can be pressed
                cont = menu[1].get_rect()
                cont = pygame.Rect(90,150,cont.width,cont.height)

                exiting = menu[2].get_rect()
                exiting = pygame.Rect(200,150,cont.width,cont.height)
           
                if cont.collidepoint(pygame.mouse.get_pos()):
                    gameState = "game"
                if exiting.collidepoint(pygame.mouse.get_pos()):
                    gameState = "menu"
        
    if gameState == "game":

        #draw the current level to the screen
        hitboxes = level.draw(player.pos[0],player.pos[1],player.dir[0],player.dir[1]
                   ,player.plane[0],player.plane[1],screen)

        if health > 0 and wave_num < len(waves):

            screen.blit(textures[14],screen.get_rect())

            #scale and position the health bar proportionally to the player's health
            healthBar = screen.get_rect()
            healthDec = health * (1/20.)
            healthBar.height = 300 * healthDec
            healthBar.y = 288 - (288 * healthDec)

            hp_texture = pygame.transform.scale(textures[16],(400,healthBar.height))

            screen.blit(textures[15],screen.get_rect())
            screen.blit(hp_texture,healthBar)


            if not current_animation == []:
                #animation automatically runs through until it ends and then goes back
                #to the first frame of the animation
                if index < len(current_animation) - 1:
                    if timer < current_animation[index][1]:
                        timer += 60 * dt
                    else:
                        timer = 0
                        index += 1
                    screen.blit(current_animation[index][0],screen.get_rect())
                else:

                    screen.blit(current_animation[0][0],screen.get_rect())


            text_image = font.render(roman_numeral(wave_num + 1), True, (255,255,255))
            text_rect = text_image.get_rect(centerx=57,centery=46)
            screen.blit(text_image, text_rect)

            text_image = font.render(str(bullets), True, (255,255,255))
            text_rect = text_image.get_rect(centerx=58,centery=273)
            screen.blit(text_image, text_rect)

            text_image = font.render('$' + str(money), True, (255,255,255))
            text_rect = text_image.get_rect(centerx=58,centery=150)
            screen.blit(text_image, text_rect)

            #render crosshair
            text_image = font.render('+', True, (255,0,0))
            text_rect = text_image.get_rect(centerx=(WIDTH / 2),centery=(HEIGHT / 2))
            screen.blit(text_image, text_rect)

            if dmg_timer > 0:
                dmg_timer -= dt
                if dmg_timer < 0:
                    dmg_timer == 0

        #render screen flash (only visible if the player was hit recently)
        frect = pygame.Surface((400,300))
        frect.set_alpha(128 * dmg_timer * 4)
        frect.fill((255,0,0))
        screen.blit(frect,(0,0))

        #if the final wave hasn't been completed
        if wave_num < len(waves):
            wave_data = waves[wave_num].update(dt, level, player.pos)

            if wave_data == 'next':
                #play the next wave
                wave_num += 1
            elif type(wave_data) == list:
                #add a new enemy
                if wave_data[2] == 0:
                    level.entities.append(enemy.Enemy(level,player.pos,wave_data[0],wave_data[1],-1,0,20,1.2,wave_data[2]))
                elif wave_data[2] == 1:
                    level.entities.append(enemy.Enemy(level,player.pos,wave_data[0],wave_data[1],-1,0,5,2,wave_data[2]))
                elif wave_data[2] == 2:
                    level.entities.append(enemy.Enemy(level,player.pos,wave_data[0],wave_data[1],-1,0,50,0.5,wave_data[2]))
                elif wave_data[2] == 3:
                    level.entities.append(enemy.Enemy(level,player.pos,wave_data[0],wave_data[1],-1,0,200,2,wave_data[2]))
                    
       
        player.dir = vector.normalized(player.dir)

        events = pygame.event.get()
        keys_pressed = pygame.key.get_pressed()

        for event in events:
            #quit if the player presses escape
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and health > 0:
                gameState = "pause"

            #switch to the primary weapon or secondary weapon depending on the number
            #the player presses
            if event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                selected_weapon = primary_weapon

                #stop animation from automatically playing
                timer = 120
                index = 120

            if event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                selected_weapon = secondary_weapon

                #stop animation from automatically playing
                timer = 120
                index = 120

            #set the right animation after switching weapons
            if selected_weapon.name == "fist":
                current_animation = fist_animation

            if selected_weapon.name == "pistol":
                current_animation = pistol_animation

            if selected_weapon.name == "rifle":
                current_animation = rifle_animation

            if selected_weapon.name == "machineGun":
                current_animation = machine_gun_animation

            #quit if the player clicks close (x)
            if event.type == pygame.QUIT:
                finish = True

        if health > 0:
            if keys_pressed[K_UP]:
                #only move on an axes if doing so does not cause an intersection
                if level.map[int(player.pos[0] + player.dir[0] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades))][int(player.pos[1])] == False:
                    player.pos[0] += player.dir[0] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades)
                if level.map[int(player.pos[0])][int(player.pos[1] + player.dir[1] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades))] == False:
                    player.pos[1] += player.dir[1] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades)

            if keys_pressed[K_DOWN]:
                #only move on an axes if doing so does not cause an intersection
                if level.map[int(player.pos[0] - player.dir[0] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades))][int(player.pos[1])] == False:
                    player.pos[0] -= player.dir[0] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades)
                if level.map[int(player.pos[0])][int(player.pos[1] - player.dir[1] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades))] == False:
                    player.pos[1] -= player.dir[1] * moveSpeed * dt * speed_multiplyer * (1.02 ** speed_upgrades)

            if keys_pressed[K_LEFT]:
                #rotate the direction and the plane so that it stays perpendicular to the direction
                player.dir = vector.rotate(player.dir,turnSpeed * dt)
                player.plane = vector.rotate(player.plane,turnSpeed * dt)

            if keys_pressed[K_RIGHT]:
                #rotate the direction and the plane so that it stays perpendicular to the direction                
                player.dir = vector.rotate(player.dir,-turnSpeed * dt)
                player.plane = vector.rotate(player.plane,-turnSpeed * dt)

        for entity in level.entities:

          #enter the shop if the player goes close enough to the object that represents it
          if health > 0 and wave_num < len(waves):
              if not entity.__class__.__name__ == "Explosion" and entity.type == 3:
                  #allow the player to move away from the shop once they exit the shop gameState
                  if vector.distance(entity.pos, [player.pos[1],player.pos[0]]) < 0.5:
                      if shop == False:
                          shop = True
                          gameState = 'shop'
                  else:
                      shop = False
            
          if entity.__class__.__name__ == "Explosion" and entity.life == 0 and entity.timer == 0:
              #the first frame that the explosion is updated
              #damage the player if they are too close to te explosion
              if vector.distance(entity.pos, [player.pos[1],player.pos[0]]) < 1.5:
                  if health >= 8 / (defense_multiplyer * (1.05 ** defense_upgrades)):
                      health -= 8 / (defense_multiplyer * (1.05 ** defense_upgrades))
                  else:
                      health = 0
                  dmg_timer = 0.35

                  knockback = random.randint(-50,50) * 0.01
                  player.dir = vector.rotate(player.dir,knockback)
                  player.plane = vector.rotate(player.plane,knockback)
          
          entity.update(dt,level,player.pos)

          #if an explosion has tagged itself to be removed, do just that
          if entity.__class__.__name__ == "Explosion":          
              if entity.remove:
                  level.entities.remove(entity)

          #subtract health if the enemy is close enough and it's attack
          #isn't cooling down      
          if vector.distance(player.pos,[entity.pos[1],entity.pos[0]]) < 0.5 and entity.__class__.__name__ == "Enemy" and health > 0 and wave_num < len(waves):
             if entity.timer == 0:
                  if health >= 3 / (defense_multiplyer * (1.05 ** defense_upgrades)):
                    health -= 3 / (defense_multiplyer * (1.05 ** defense_upgrades))
                  else:
                    health = 0
                  dmg_timer = 0.25
                  
                  knockback = random.randint(-50,50) * 0.01
                  player.dir = vector.rotate(player.dir,knockback)
                  player.plane = vector.rotate(player.plane,knockback)
                  
                  entity.timer = 1

        if fire_timer > 0:
            fire_timer -= 60 * dt
            if fire_timer < 0:
                fire_timer = 0

        #hitboxes will be in order from furthest to closest, reverse the order
        #so that bullet penetration logic can work
        hitboxes = hitboxes[::-1]

        #attack if there are bullets to fire or the current weapon is a melee weapon
        #and the space bar is pressed
        if keys_pressed[K_SPACE] and (bullets > 0 or selected_weapon.type == "melee") and fire_timer == 0:

            if selected_weapon.name == "fist":
                current_animation = fist_animation
                index = 0
                timer = 0

            if selected_weapon.name == "pistol":
                current_animation = pistol_animation
                index = 0
                timer = 0

            if selected_weapon.name == "rifle":
                current_animation = rifle_animation
                index = 0
                timer = 0

            if selected_weapon.name == "machineGun":
                current_animation = machine_gun_animation
                index = 0
                timer = 0

            if selected_weapon.type == "gun":
                bullets -= 1

            fire_timer = 60 / selected_weapon.fireRate
            enemies_hit = 0

            for hitbox in hitboxes:
                if (WIDTH / 2) > hitbox[0] and (WIDTH / 2) < hitbox[1] and enemies_hit < selected_weapon.penetration:

                    if hitbox[2].__class__.__name__ == "Enemy":

                        #check that the conditions of hitting with the weapon are satisfied
                        if (selected_weapon.type == "melee" and vector.distance([hitbox[2].pos[1],hitbox[2].pos[0]],player.pos) < 1) or selected_weapon.type == "gun":
                            hitbox[2].damage(selected_weapon.damage)
                            enemies_hit += 1

                            #remove the entity if it is dead
                            if hitbox[2].health <= 0:
                                level.entities.remove(hitbox[2])
                                if selected_weapon.type == "gun":
                                    money += 5
                                else:
                                    money += 15

                                #create an explosion if the type of enemy is explosive
                                if hitbox[2].type == 5:
                                    level.entities.append(enemy.Explosion(hitbox[2].pos[0],hitbox[2].pos[1]))

        if health == 0 or wave_num >= len(waves):
            trans_timer -= dt
            if trans_timer < 0:
                if wave_num >= len(waves):
                    gameState = "win"
                if health == 0:
                    gameState = "death"

    pygame.display.flip()

    #tells pygame to handle internal events automatically
    pygame.event.pump()


pygame.quit()


