''''
Network handling
Altough the use of both tcp and udp is discouraged due to packet loss in udp from the tcp trafic
we still use this method as the tcp packets are in tiny amount compared to udp
'''

import struct

""" 
Packets data definition
"""

#PROTOCOLS

UDP = 0
TCP = 1

UDP_PORT = 53638
TCP_PORT = 53639

PLAYER_CONNECT    = 1
ENTITY_SPAWN      = 2
ENTITY_MVT_DATA   = 3
ENTITY_STATE      = 4
ENTITY_FOCUS      = 5
PLAYER_HEAD_DIRECTION = 6

PACKET_DATA = {
    PLAYER_CONNECT                  : "iS",      # game version, player name
    ENTITY_SPAWN                    : "iiii",    # entityType, entityId, x, y
    ENTITY_MVT_DATA                 : "iiiiiii", #entityId, x, y, vx, vy, ax, ay
    ENTITY_STATE                    : "iil",     #entityId, stateId, stateStep
    ENTITY_FOCUS                    : "ic",      #entityId, isThePlayer
    PLAYER_HEAD_DIRECTION           : "id"       #entityID, the rotation
}

PACKET_PROTOCOL = {
    PLAYER_CONNECT: TCP,
    ENTITY_SPAWN: TCP,
    ENTITY_STATE: TCP,
    ENTITY_FOCUS: TCP,
    
    ENTITY_MVT_DATA : UDP,
    PLAYER_HEAD_DIRECTION: UDP
}


class NetHandler:
    """
    Handles the network between a server a client
    All the packets first carries their packet id
    The packets over UDP have a instruction number (IN)
        an incoming udp packet will be disregarded if its IN is < greatest received IN from server
    """
    
    pass
    
    
    
    
    
    
    
    
    
    
