"""Skill: kasa — Kasa smart plugs."""

SKILL = {
    "name": "kasa",
    "description": "Control Kasa smart plugs",
    "config": {
        "coffee_bar_lights": {
            "type": "text",
            "default": "Coffee Bar Lights",
            "description": "Kasa device name for coffee bar lights",
        },
        "coffee_machine": {
            "type": "text",
            "default": "Espresso Machine",
            "description": "Kasa device name for espresso machine",
        },
    },
    "prompt": """kasa
    Triggers: Use when the user wants to control Kasa smart plugs or ask about their status.
      * "Turn on the coffee machine"
      * "Turn off the espresso machine"
      * "Turn on the coffee bar lights"
      * "Turn off the coffee bar lights    
    Example: {{"function": "kasa", "parameters": {{"device_name": "coffee_machine", "action": "off"}}}}""",
    "examples": [
        """Example - Turn on coffee or espresso machine:
User: "Turn on my coffee machine"
Response: {{"reply": "Turning on coffee machine", "function_calls": [{{"function": "kasa", "parameters": {{"device_name": "coffee_machine", "action": "on"}}}}], "new_memories": []}}""",
        """Example - Turn on or off the coffee bar lights:
User: "Turn on my coffee bar lights"
Response: {{"reply": "Turning on coffee bar lights", "function_calls": [{{"function": "kasa", "parameters": {{"device_name": "coffee_bar_lights", "action": "on"}}}}], "new_memories": []}}""",
    ],
}


def execute(parameters, context):
    from modules.module_messageQue import queue_message
    from modules.module_kasa import turn_on, turn_off

    skill_config = context.get("skill_config", {})

    queue_message(f"parameters: {parameters}")

    device_name = skill_config.get(parameters.device_name, {})
    if parameters.action == "on":
        turn_on(device_name)
        queue_message(f"Turning on {device_name}")
        return f"Turning on {device_name}"
    elif parameters.action == "off":
        turn_off(device_name)
        queue_message(f"Turning off {device_name}")
        return f"Turning off {device_name}"

    return "I didn't understand your request."
