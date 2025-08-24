# ===== 基礎版事件清單（事件 + 效果 + 道具 + 金錢） =====
qi_training_events = [
    {"text": "你在洞府中打坐調息，靈氣周天運轉更為順暢。", "effect": {"qi": 5}, "items": [], "money": 0},
    {"text": "你參悟經典，對靈氣掌控更進一層。", "effect": {"qi": 5}, "items": [], "money": 0},
    {"text": "你服用清心散，心境沉穩如磐，靈氣略有精進。", "effect": {"qi": 5}, "items": [{"name": "清心散", "type": "丹藥"}], "money": 0},
    {"text": "你捕捉到一縷天地元氣，融入丹田。", "effect": {"qi": 5}, "items": [], "money": 5},
    {"text": "你以意馭氣，小有所成。", "effect": {"qi": 5}, "items": [], "money": 0}
]

qi_expedition_events = [
    {"text": "你在靈脈附近駐足，靈氣如潮湧入體內。", "effect": {"qi": 10}, "items": [], "money": 10},
    {"text": "你獲得一株靈草，藥力化開，靈氣暴漲。", "effect": {"qi": 10}, "items": [{"name": "靈草", "type": "草藥"}], "money": 0},
    {"text": "你遇見高人指點一二，對氣機流轉頗有心得。", "effect": {"qi": 10}, "items": [], "money": 0},
    {"text": "你於月下運功，吸納月華，靈氣精純。", "effect": {"qi": 10}, "items": [], "money": 0},
    {"text": "你在古陣間淬鍊靈氣，丹田更加澄澈。", "effect": {"qi": 10}, "items": [{"name": "陣法符紙", "type": "道具"}], "money": 0}
]

body_training_events = [
    {"text": "你以鐵砂功煉皮膜，血氣鼓蕩。", "effect": {"blood": 5}, "items": [], "money": 0},
    {"text": "你吞吐粗息淬鍊筋骨，渾身暖流奔湧。", "effect": {"blood": 5}, "items": [], "money": 0},
    {"text": "你以樁功立身，根基更穩，血脈更盛。", "effect": {"blood": 5}, "items": [], "money": 0},
    {"text": "你以重器負重演拳，骨節發響如雷。", "effect": {"blood": 5}, "items": [{"name": "重器", "type": "修煉器具"}], "money": 0},
    {"text": "你以藥浴溫養血肉，血氣更為厚重。", "effect": {"blood": 5}, "items": [{"name": "溫養藥液", "type": "丹藥"}], "money": 0}
]

body_expedition_events = [
    {"text": "你於瀑下負重抗水，體魄更勝往昔。", "effect": {"blood": 10}, "items": [], "money": 0},
    {"text": "你入山與猛獸對垒，雖疲憊卻血氣昌盛。", "effect": {"blood": 10}, "items": [], "money": 20},
    {"text": "你獲得一枚淬體丹，藥力化開血脈。", "effect": {"blood": 10}, "items": [{"name": "淬體丹", "type": "丹藥"}], "money": 0},
    {"text": "你攀崖練指，虎口生繭，血肉更堅實。", "effect": {"blood": 10}, "items": [], "money": 0},
    {"text": "你以烈日曝曬行罡步，汗出如漿而血氣更旺。", "effect": {"blood": 10}, "items": [], "money": 0}
]

# 大境界
realms_power = ["淬體", "武徒", "武士", "武師", "大武師",
                "武王", "武皇", "武帝", "武尊", "武聖"]
realms_mana = ["練氣", "築基", "結丹", "元嬰", "化神",
               "煉虛", "合體", "大乘", "渡劫", "真仙"]

# 靈根品級
talent_level = {"下品": 0.7, "中品": 0.2, "上品": 0.099, "極品": 0.001}
talent = {"金靈根": 0.11, "木靈根": 0.11, "水靈根": 0.11, "火靈根": 0.11,
          "土靈根": 0.11, "風靈根": 0.11, "雷靈根": 0.11, "毒靈根": 0.11,
          "偽靈根": 0.11, "仙靈根": 0.01}