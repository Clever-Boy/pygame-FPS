import math
import world
import enemy

class Wave():

    def __init__(self, enemies, delay):

        self.enemyData = enemies
        
        #time allowed between spawn (secs)
        self.spawnInterval = delay

        #tracks time since last spawn
        self.timer = 0

        #tracks how many enemies have been spawned
        self.spawnNum = 0

        #delay before enemies will start to spawn
        self.beginTimer = 10

    def update(self, dt, level, playerPos):

        if self.beginTimer > 0:
            self.beginTimer -= dt
            
            #the beginning timer is still ticking down
            return 'rest'
        else:

            if not self.spawnNum == len(self.enemyData):
                #increment the timer
                self.timer -= dt

                #when the timer passes the spawn delay, reset it
                #and spawn a new enemy into the level
                if self.timer <= 0:
                    self.timer = self.spawnInterval
                    self.spawnNum += 1

                    #return data neccessary for spawning an enemy
                    return level.spawn_enemy(playerPos,self.enemyData[self.spawnNum - 1])

            else:
                #check all entities to see if they are enemies because
                #entities can be other things
                for entity in level.entities:
                    if entity.__class__.__name__ == 'Enemy':
                        #enemy found, keep playing the wave
                        return 'wait'
                #no enemies found, start the next wave
                return 'next'

            
      
                    
            
        
    
    
    


