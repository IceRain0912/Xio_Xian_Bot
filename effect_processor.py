# effect_processor.py

def apply_effect(player, event):
    for k, v in event["effect"].items():
        player[k] = player.get(k, 0) + v
    if event.get("money", 0):
        player["money"] = player.get("money", 0) + event["money"]
