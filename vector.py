import math
#vectors are arrays containing x,y and z values eg. [0.2,1]

#returns a vector with no information
def zero():
    return [0,0,0]

#returns the negative equivilent of the vector
def negative(v):
    return [-v[0],-v[1]]

#returns the resultant of adding two vectors together
def add(a,b):
    return [a[0] + b[0], a[1] + b[1]]

#returns the length of a vector
def length(v):
    return math.sqrt((v[0]**2) + (v[1]**2))

#returns the distance between two vectors
def distance(a,b):
    resultant = add(b,negative(a))
    return length(resultant)

#returns a vector with the same direction, but with a length of 1
def normalized(v):
    leng = length(v)

    if leng == 0:
        return [0,0]
    else:
        return [v[0] / leng, v[1] / leng]

#smoothly transition between two vectors by the ratio 't'
def lerp(a,b,t):
    return [(b[0] - a[0]) / t,(b[1] - a[1]) / t]

#smoothly transition between two unit vectors,
#and clamp the length of the resultant
def slerp(a,bt):
    original_length = length(a)
    resultant = lerp(a,b,t)
    ratio = original_length / length(resultant)
    return [resultant[0] * ratio, resultant[1] * ratio]

#returns vector v around the z axis by r in degrees
def rotate(v,r):
    #identical to a 2d rotation matrix
    sn = math.sin(r)
    cs = math.cos(r)
    nx = (v[0] * cs) - (v[1] * sn)
    ny = (v[0] * sn) + (v[1] * cs)
    return [nx,ny]
    


