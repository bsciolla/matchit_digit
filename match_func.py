

#!/usr/bin/env python



#Import Modules
import numpy


def testing():
    tiles = numpy.random.randint(0,NKEYS,size=(6,6))
    tiles[1,:] = -1
    tiles[1,0] = 5
    
    assert(is_free_cw_angle_from_to(0,1,4,1,tiles))
    assert(is_free_ccw_angle_from_to(0,1,4,1,tiles))
    assert(is_free_cw_angle_from_to(4,1,0,1,tiles))
    assert(is_free_cw_angle_from_to(0,1,4,2,tiles))
    assert(is_free_cw_angle_from_to(0,1,4,3,tiles) == False)
    
    tiles[2,4] = -1
    assert(is_free_cw_angle_from_to(0,1,4,3,tiles))
    
    tiles[:,3] = -1
    
    assert(is_free_cw_angle_from_to(0,1,3,5,tiles))
    assert(is_free_ccw_angle_from_to(0,1,3,5,tiles) == False)

    tiles = numpy.random.randint(0,NKEYS,size=(6,6))
    tiles[:,1] = -1
    assert(is_free_cw_angle_from_to(1,1,1,4,tiles))
    assert(is_free_ccw_angle_from_to(1,1,1,4,tiles))
    assert(is_free_ccw_angle_from_to(1,4,1,1,tiles))


    
def find_connection(i, j, it, jt, tiles):
    #print("searching :", i,j , "  to ", it, jt)
    # Always flip array such that it >= i and jt >= j (LAZY)
    hblock = tiles.shape[1]
    vblock = tiles.shape[0]
    
    if i > it:
        tiles = numpy.flip(tiles, axis=1)
        i,it = hblock-1-i, hblock-1-it
    if j > jt:
        tiles = numpy.flip(tiles, axis=0)
        j,jt = vblock-1-j, vblock-1-jt
    
    
    found = False
    
    if (abs(i-it) == 1 and j==jt) or (abs(j-jt) == 1 and i==it):
        return(True)
       
    if is_free_cw_angle_from_to(i, j, it, jt, tiles) or \
        is_free_ccw_angle_from_to(i, j, it, jt, tiles):
        #print("direct")
        return(True)

    # Bug case of aligned horizontally
    if jt == j:
        if numpy.all(tiles[j,i+1:it] == -1):
            return(True)
        

    # Case left
    il = i - 1
    while (tiles[j,il] == -1):
        if is_free_ccw_angle_from_to(il, j, it, jt, tiles):
            found = True
            break
        il = il - 1
        if il<0:
            break

    
    # Case right
    il = i + 1
    while (tiles[j,il] == -1):
    
        if il <= it:
            if is_free_ccw_angle_from_to(il, j, it, jt, tiles):
                found = True
               # print("ccw right", il,j,it,jt)
                break
        else:
            if is_free_cw_angle_from_to(il, j, it, jt, tiles):
                found = True
               # print("cw right", il,j,it,jt)
                break
        il = il + 1
        if il>hblock-1:
            break
    #if found == True:
     #   print('right')
        
    # Case up
    jl = j - 1
    while (tiles[jl,i] == -1):
        if is_free_cw_angle_from_to(i, jl, it, jt, tiles):
            found = True
            break
        jl = jl - 1
        if jl<0:
            break

        
    # Case down
    jl = j + 1
    while (tiles[jl,i] == -1):
        if jl <= jt:
            if is_free_cw_angle_from_to(i, jl, it, jt, tiles):
                found = True
                break
        else:
            if is_free_ccw_angle_from_to(i, jl, it, jt, tiles):
                found = True
                break
        jl = jl + 1
        if jl>vblock-1:
            break

        
    return(found)
            
    
def is_free_cw_angle_from_to(i, j, it, jt, tiles):
 
 # O>-|    or   O
 #    v         v
 #    X     X-<--
 
    if jt<j:
        print("unexpected in cw")
    if i <= it:
#        trace = numpy.all(tiles[j,i+1:it] == -1) and \
#            numpy.all(tiles[j:jt,it] == -1)
         trace = is_free_horizontal(i+1,it,j,tiles) and \
                is_free_vertical(j+1,jt-1,it,tiles)
            
    else:
        trace = is_free_vertical(j+1,jt,i,tiles) and \
                is_free_horizontal(it+1,i-1,jt,tiles)
#        trace = numpy.all(tiles[j+1:jt+1,i] == -1) and \
#            numpy.all(tiles[jt,it+1:i] == -1)
    
    return(trace)


def is_free_ccw_angle_from_to(i, j, it, jt, tiles):
 
 #     X    or   O
 #     |         v
 # 0->--         -->-X
    if it<i:
        print("unexpected in ccw")
    if jt <= j:
#        trace = numpy.all(tiles[j,i+1:it+1] == -1) and \
#            numpy.all(tiles[jt+1:j,it] == -1)
        trace = is_free_horizontal(i+1,it,j,tiles) and \
                is_free_vertical(jt+1,j-1,it,tiles)
            
    else:
#        trace = numpy.all(tiles[j+1:jt+1,i] == -1) and \
#            numpy.all(tiles[jt,i:it] == -1)
        trace = is_free_vertical(j+1,jt,i,tiles) and \
                is_free_horizontal(i,it-1,jt,tiles)
    return(trace)
            
def is_free_horizontal(i,it,j,tiles):
    if it<i:
        return True
    return(numpy.all(tiles[j,i:it+1]==-1))
            
def is_free_vertical(j,jt,i,tiles):
    if jt<j:
        return True
    return(numpy.all(tiles[j:jt+1,i]==-1) )

