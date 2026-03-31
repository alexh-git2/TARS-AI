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
    Example: {{"function": "kasa", "parameters": {{"prompt": "Turn on my coffee machine"}}}}""",
    "examples": [
        """Example - Turn on coffee or espresso machine:
User: "Turn on my coffee machine"
Response: {{"reply": "Turning on coffee machine", "function_calls": [{{"function": "kasa", "parameters": {{"kitchen": "espresso machine", "action": "coffee_machine"}}}}], "new_memories": []}}""",
        """Example - Turn on or off the coffee bar lights:
User: "Turn on my coffee bar lights"
Response: {{"reply": "Turning on coffee bar lights", "function_calls": [{{"function": "kasa", "parameters": {{"kitchen": "coffee bar lights", "action": "coffee_bar_lights"}}}}], "new_memories": []}}""",
    ],
}


def execute(parameters, context):
    from modules.module_messageQue import queue_message

    skill_config = context.get("skill_config", {})

    queue_message(f"parameters: {parameters}")

    device_name = skill_config.get("coffee_bar_lights", {})
    queue_message(f"devname={device_name}")
    return "I couldn't get a response from Kasa."
