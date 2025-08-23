# event.py
import random

qi_training_events = [
    {"text": "你在洞府中打坐調息，靈氣周天運轉更為順暢。", "effect": {"qi": 5}, "items": [], "money": 0},
    {"text": "你參悟經典，對靈氣掌控更進一層。", "effect": {"qi": 5}, "items": [], "money": 0},
    {"text": "你服用清心散，心境沉穩如磐，靈氣略有精進。", "effect": {"qi": 5}, "items": [{"name": "清心散"}], "money": 0}
]

qi_expedition_events = [
    {"text": "你在靈脈附近駐足，靈氣如潮湧入體內。", "effect": {"qi": 10}, "items": [], "money": 10},
    {"text": "你獲得一株靈草，藥力化開，靈氣暴漲。", "effect": {"qi": 10}, "items": [{"name": "靈草"}], "money": 0}
]

body_training_events = [
    {"text": "你以鐵砂功煉皮膜，血氣鼓蕩。", "effect": {"blood": 5}, "items": [], "money": 0},
    {"text": "你吞吐粗息淬鍊筋骨，渾身暖流奔湧。", "effect": {"blood": 5}, "items": [], "money": 0}
]

body_expedition_events = [
    {"text": "你於瀑下負重抗水，體魄更勝往昔。", "effect": {"blood": 10}, "items": [], "money": 0},
    {"text": "你入山與猛獸對垒，雖疲憊卻血氣昌盛。", "effect": {"blood": 10}, "items": [], "money": 20}
]

def get_random_event(direction, type_):
    if direction == "煉氣":
        if type_ == "training":
            return random.choice(qi_training_events)
        else:
            return random.choice(qi_expedition_events)
    else:
        if type_ == "training":
            return random.choice(body_training_events)
        else:
            return random.choice(body_expedition_events)
