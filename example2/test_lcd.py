#!/usr/bin/env python3

import time
import random

from litex import RemoteClient

wb = RemoteClient()
wb.open()

# # #

# Test led
print("Testing Led...")
for i in range(480):
    if (i<60):
        color = 0x00000000 #black
    elif ((i<120)):    
         color = 0x001F001F #blue
    elif ((i<180)):    
         color = 0xF800F800 #red
    elif ((i<240)):    
         color = 0x7E007E00 #green
    elif (i<300):    
         color = 0x07FF07FF #Cyne
    elif (i<360):    
         color = 0xF81FF81F # Magenta
    elif (i<420):    
         color = 0xFFE0FFE0 # Yellow
    else:    
         color = 0xFFFFFFFF # White
    wb.write(0x1000+4*i,color)



# # #

wb.close()
