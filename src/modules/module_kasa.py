"""
module_kasa.py

Kasa smart switch control for TARS-AI.
"""
import asyncio
from kasa import Discover, Device
from kasa.device import Device
from typing import Dict

from modules.module_messageQue import queue_message
 
_coffee_bar_lights: Device
_espresso_machine: Device

def turn_on_coffeebar():
   if _coffee_bar_lights:
       asyncio.run(_coffee_bar_lights.turn_on())
       
def turn_off_coffeebar():
   if _coffee_bar_lights:
       asyncio.run(_coffee_bar_lights.turn_off())

def turn_on_espresso_machine():
    if _espresso_machine:
        asyncio.run(_espresso_machine.turn_on())

def turn_off_espresso_machine():
    if _espresso_machine:
        asyncio.run(_espresso_machine.turn_off())
                      
async def main():    
    queue_message("[KASA] initializing...")
    devices = await Discover.discover()
    global _coffee_bar_lights
    global _espresso_machine
    for ip, dev in devices.items():
        await dev.update()  # get full info if you want alias, state, etc.
        # print(f"{ip} -> ({dev.model}), On: {dev.is_on} Alias: {dev.alias}")
        
        if dev.alias.lower().strip() == "coffee bar lights":
            _coffee_bar_lights = dev

        if dev.alias.lower().strip() == "espresso machine":
            _espresso_machine = dev
            
        
def start_kasa():
    asyncio.run(main())