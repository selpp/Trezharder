'''
Created on 27 nov. 2017

@author: WIN32GG
'''

import sys

"""
    DEBUG OUTPUT HANDLING
"""
#debug level 0,1,2,3 the higher, the depper debug
_DEBUG_LEVEL = 3
_DEBUG_DICT  = {0:"Minimum", 1: "Simple", 2: "In-depth", 3: "Everything"}

#call example: debug("Debug message", 0, True)  prints an error message in stderr

def debug(msg, level = 1, err = False):
    stream = sys.stderr if err else sys.stdout
    msg    = "[ERROR] "+msg if err else "[INFO] "+msg
    if(level <= _DEBUG_LEVEL):
        stream.write(msg+"\n")
        stream.flush()
		
		