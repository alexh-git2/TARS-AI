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
    MANDATORY: Always call function when user asks turn on or turn off coffee machine, espresso machine, or coffee bar lights
    Triggers: Use when the user wants to control Kasa smart plugs or ask about their status.
      * User wants to turn on or off their coffee or espresso machine
      * User wants to turn on or off their coffee bar lights
    Example: {{"function": "kasa", "parameters": {{"device": "coffee_machine", "action": "off"}}}}""",
    "examples": [
        """Example - Turn on coffee machine:
User: "Turn on coffee machine"
Response: {{"reply": "Turning on coffee machine", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_machine", "action": "on"}}}}], "new_memories": []}}""",
        """Example - Turn off coffee machine:
User: "Turn off coffee machine"
Response: {{"reply": "Turning off coffee machine", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_machine", "action": "off"}}}}], "new_memories": []}}""",
        """Example - Turn on espresso machine:
User: "Turn on espresso machine"
Response: {{"reply": "Turning on espresso machine", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_machine", "action": "on"}}}}], "new_memories": []}}""",
        """Example - Turn off espresso machine:
User: "Turn off espresso machine"
Response: {{"reply": "Turning off espresso machine", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_machine", "action": "off"}}}}], "new_memories": []}}""",
        """Example - Turn on coffee bar lights:
User: "Turn on coffee bar lights"
Response: {{"reply": "Turning on coffee bar lights", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_bar_lights", "action": "on"}}}}], "new_memories": []}}""",
        """Example - Turn off coffee bar lights:
User: "Turn off coffee bar lights"
Response: {{"reply": "Turning off coffee bar lights", "function_calls": [{{"function": "kasa", "parameters": {{"device": "coffee_bar_lights", "action": "off"}}}}], "new_memories": []}}""",
    ],
}


def execute(parameters, context):
    from modules.module_messageQue import queue_message
    from modules.module_kasa import turn_on, turn_off

    skill_config = context.get("skill_config", {})

    device = parameters.get("device", "")
    device_name = skill_config.get(device, {})
    action = parameters.get("action", "")
    if action == "on":
        turn_on(device_name)
        queue_message(f"Turning on {device_name}")
        return f"Turning on {device_name}"
    elif action == "off":
        turn_off(device_name)
        queue_message(f"Turning off {device_name}")
        return f"Turning off {device_name}"

    return "I didn't understand your request."
