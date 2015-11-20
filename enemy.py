import math
import vector
import world

class Enemy(world.Entity):

    def line_of_sight(self,level,playerPos):

        #check all nodes between the player and the enemy to see if there
        #is a wall in the way

        rel = vector.normalized(vector.add([playerPos[1],playerPos[0]],vector.negative(self.pos)))
        checkPos = self.pos

        for i in 10 * range(int(math.floor(vector.distance([playerPos[1],playerPos[0]],self.pos))) - 1):
            checkPos = vector.add(checkPos,[rel[0] * 0.1,rel[1] * 0.1])
            if not level.map[int(math.floor(checkPos[1]))][int(math.floor(checkPos[0]))] == 0:
                return False
        return True


    def find_path(self,level,playerPos):
        
        gridX = int(self.pos[0])
        gridY = int(self.pos[1])

        playerGridX = int(playerPos[1])
        playerGridY = int(playerPos[0])

        #array to generate values to
        search = [[-1 for x in range(len(level.map[0]))] for y in range(len(level.map[0]))]

        #nodes to check adjacent to
        check = []
        
        search[gridY][gridX] = 0
        
        check.append([gridX,gridY,0])

        checkX = gridX
        checkY = gridY

        node = check[0]
       
        while not (checkX == playerGridX and checkY == playerGridY):
            
            node = check[0]
            
            checkX = node[0]
            checkY = node[1]
            if not(checkX == playerGridX and checkY == playerGridY):
                #check that the item doesn't already have a value generated to it and
                #that the item in the level isn't a wall
                #do this for all adjacent nodes
                if search[checkY][checkX + 1] == -1 and level.map[checkY][checkX + 1] == 0:
                    search[checkY][checkX + 1] = node[2] + 1
                    check.append([checkX + 1,checkY,node[2] + 1])
                if search[checkY + 1][checkX] == -1 and level.map[checkY + 1][checkX] == 0:
                    search[checkY + 1][checkX] = node[2] + 1
                    check.append([checkX,checkY + 1,node[2] + 1])
                if search[checkY][checkX - 1] == -1 and level.map[checkY][checkX - 1] == 0:
                    search[checkY][checkX - 1] = node[2] + 1
                    check.append([checkX - 1,checkY,node[2] + 1])
                if search[checkY - 1][checkX] == -1 and level.map[checkY - 1][checkX] == 0:
                    search[checkY - 1][checkX] = node[2] + 1
                    check.append([checkX,checkY - 1,node[2] + 1])
                check.remove(node)
 
        currentX = playerGridX
        currentY = playerGridY      
        
        while not(currentX == gridX and currentY == gridY):

            adjacent = []

            #find the smallest value of the adjacent items on the search array
            if search[currentY][currentX + 1] > -1:
                adjacent.append([search[currentY][currentX + 1],currentY,currentX + 1])
            if search[currentY + 1][currentX] > -1:
                adjacent.append([search[currentY + 1][currentX],currentY + 1,currentX])
            if search[currentY][currentX - 1] > -1:
                 adjacent.append([search[currentY][currentX - 1],currentY,currentX - 1])
            if search[currentY - 1][currentX] > -1:
                adjacent.append([search[currentY - 1][currentX],currentY - 1,currentX])

            adjacent = sorted(adjacent)
                
            #add node to the enemy's nodes array for movement
            self.nodes.append([adjacent[0][2] + 0.5,adjacent[0][1] + 0.5])

            currentX = adjacent[0][2]
            currentY = adjacent[0][1]
       
        
    def __init__(self,level,playerPos,px,py,dx,dy,h,s,typ):
        self.pos = [px,py]
        self.dir = [dx,dy]
        
        #add 4 to the type because 0-3 take up the objects in the game
        self.type = typ + 4
        
        self.health = h
        self.speed = s

        #ordered list of vectors that create a path towards the target (always the player)
        self.nodes = []

        self.timer = 0

        self.find_path(level,playerPos)

    def update(self,dt,level,playerPos):
        
        if self.timer > 0:
            self.timer -= 1 * dt
            if self.timer < 0:
                self.timer = 0
            
        relplayer = vector.add([playerPos[1],playerPos[0]],vector.negative(self.pos))

        if self.line_of_sight(level,playerPos):
            #move directly at the player if they can be seen
            if vector.length(relplayer) > 0.2:
              reldir = vector.normalized(relplayer)
              self.pos = vector.add(self.pos,[reldir[0] * self.speed * dt, reldir[1] * self.speed * dt])

        else:

            #update the target position if the player moves to far away
            #from the original target position
            if len(self.nodes) == 0 or vector.distance(self.pos,self.nodes[len(self.nodes) - 1]) > 2:
                self.find_path(level,playerPos)    
            else:
                #get the direction to move in
                rel = vector.add(self.nodes[len(self.nodes) - 1],vector.negative(self.pos))

                #set the position to the vector if moving one step will cause
                #the enemy to move over the node
                if vector.length(rel) < self.speed * dt:
                    self.pos = self.nodes[len(self.nodes) - 1]
                    #return subset of original that doesn't include the first entry
                    self.nodes.remove(self.nodes[len(self.nodes) - 1])
                else:
                    
                    #move towards the node
                    rel = vector.normalized(rel)
                    self.pos = vector.add(self.pos,[rel[0] * self.speed * dt,rel[1] * self.speed * dt])

    def damage(self,amount):
        self.health -= amount 
                
class Explosion(world.Entity):

    def __init__(self,px,py):
        self.pos = [px,py]
        self.timer = 0
        self.life = 0
        self.remove = False
        
    def update(self,dt,level,playerPos):
        self.timer += dt
        if self.timer > 0.1:
            self.timer = 0
            self.life += 1
            if self.life > 2:
                self.remove = True
                
        
                
        
        
              
            
        
        


