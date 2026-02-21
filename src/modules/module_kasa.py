"""
module_kasa.py

Kasa smart switch control for TARS-AI.
"""
import asyncio
from kasa import Discover, Device
from kasa.device import Device
from typing import Dict
from modules.module_config import load_config
from modules.module_messageQue import queue_message
 
CONFIG = load_config()
 
_coffee_bar_lights: Device
_espresso_machine: Device

async def _turn_on(plug: Device):
    if plug:
        await plug.update()
        await plug.turn_on()
        
    
async def _turn_off(plug: Device):
    if plug:
        await plug.update()
        await plug.turn_off()
    
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
        if dev.alias.lower().strip() == CONFIG["KASA"]["coffee_bar_lights"]:
            _coffee_bar_lights = dev

        if dev.alias.lower().strip() == CONFIG["KASA"]["espresso_machine"]:
            _espresso_machine = dev
            
        
def start_kasa():
    asyncio.run(main())