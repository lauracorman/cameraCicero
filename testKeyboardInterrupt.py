# -*- coding: utf-8 -*-
"""
Created on Thu Aug 06 14:06:26 2015

@author: maintenancelab
"""
from time import sleep
i = 0
try:
    while True:
        print i
        i = i+1
        sleep(1)
except KeyboardInterrupt:
    print 'c\'est fini'