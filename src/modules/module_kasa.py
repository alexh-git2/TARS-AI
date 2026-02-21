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

_retry_count = 3
_delay = 0.5

async def _turn_on(plug: Device):
    for attempt in range(1, _retry_count + 1):
        try:
            if plug:
                await plug.turn_on()
                await plug.update()
            return
        except:
            # print(f"[Attempt {attempt}] Communication error: {e}")
            if attempt == retries:
                raise
            await asyncio.sleep(_delay)
    
async def _turn_off(plug: Device):
    for attempt in range(1, _retry_count + 1):
        try:
            if plug:
                await plug.turn_off()
                await plug.update()
            return
        except:
            # print(f"[Attempt {attempt}] Communication error: {e}")
            if attempt == retries:
                raise
            await asyncio.sleep(_delay)  
    
def turn_on_coffeebar():
    asyncio.run(_turn_on(_coffee_bar_lights))

def turn_off_coffeebar():
    asyncio.run(_turn_off(_coffee_bar_lights)) 

def turn_on_espresso_machine():
    asyncio.run(_turn_on(_espresso_machine))

def turn_off_espresso_machine():
    asyncio.run(_turn_off(_espresso_machine))
                      
async def main():    
    queue_message("[KASA] initializing...")
    devices = await Discover.discover()
    global _coffee_bar_lights
    global _espresso_machine
    
    for ip, dev in devices.items():
        await dev.update()  # get full info if you want alias, state, etc.
        #print(f"{ip} -> ({dev.model}), On: {dev.is_on} Alias: {dev.alias}")

        if dev.alias.lower().strip() == CONFIG["KASA"]["coffee_bar_lights"].lower().strip():
            _coffee_bar_lights = dev

        if dev.alias.lower().strip() == CONFIG["KASA"]["espresso_machine"].lower().strip():
            _espresso_machine = dev
            
        asyncio.sleep(_delay)
            
        
def start_kasa():
    asyncio.run(main())