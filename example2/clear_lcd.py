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
  color = 0x001F001F #black
  wb.write(0x1000+4*i,color)

# # #

wb.close()
