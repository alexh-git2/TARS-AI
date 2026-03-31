"""
module_kasa.py

Kasa smart switch control for TARS-AI.
"""

import asyncio
import os
from kasa import Discover, Device
from typing import Dict
from modules.module_config import load_config
from modules.module_messageQue import queue_message
import os

CONFIG = load_config()

_retry_count = 3
_delay = 0.5

_devices: Dict[str, Device] = {}


async def _turn_on(plug: Device):
    for attempt in range(1, _retry_count + 1):
        try:
            if plug:
                await plug.turn_on()
                await plug.update()
            return
        except:
            # print(f"[Attempt {attempt}] Communication error: {e}")
            if attempt == _retry_count:
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
            if attempt == _retry_count:
                raise
            await asyncio.sleep(_delay)


def turn_on(name):
    global _devices
    kasa_device = _devices.get(name)
    if kasa_device is not None:
        asyncio.run(_turn_on(kasa_device))
    else:
        queue_message(f"Kasa device '{name}' not found.")


def turn_off(name):
    global _devices
    kasa_device = _devices.get(name)
    if kasa_device is not None:
        asyncio.run(_turn_off(kasa_device))
    else:
        queue_message(f"Kasa device '{name}' not found.")


async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    username = os.getenv("KASA_USERNAME")
    password = os.getenv("KASA_PASSWORD")
    devices = await Discover.discover(username=username, password=password)
    global _devices
    global _delay

    for ip, dev in devices.items():
        try:
            await dev.update()  # get full info if you want alias, state, etc.
            print(f"{ip} -> ({dev.model}), On: {dev.is_on} Alias: {dev.alias}")
            _devices[f"{dev.alias}"] = dev
            await asyncio.sleep(_delay)
        except Exception as e:
            queue_message(f"module_kasa: {e}")


def start_kasa():
    print("[KASA] Initializing Kasa module...")
    asyncio.run(main())
