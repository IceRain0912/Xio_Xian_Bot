import discord
from discord.ext import commands
import random
import json
import os
from dotenv import load_dotenv
from event import *
from items import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# 玩家數據
players = {}
DATA_FILE = "players.json"

# --- JSON 儲存與載入 ---
def load_players():
    global players
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            players = json.load(f)
        players = {int(k): v for k, v in players.items()}
        print("玩家資料已載入")
    else:
        players = {}

def save_players():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

# --- 小工具：建立進度條 (ANSI 文字) ---
def create_status_bar(value, max_value, color):
    filled = int((value / max_value) * 20)
    empty = 20 - filled
    bar = f"[{'█'*filled}{'░'*empty}] {value}/{max_value}"
    return f"```ansi\n\u001b[{color}m{bar}\u001b[0m```"

# --- 狀態 embed ---
def build_status_embed(user, player):
    qi = player.get("qi", 0)
    blood = player.get("blood", 0)
    max_qi = player.get("max_qi", 100)
    max_blood = player.get("max_blood", 100)

    def realm_text(direction, level_index, sub_level):
        if direction == "煉氣":
            realm = realms_mana[level_index]
        else:
            realm = realms_power[level_index]
        return f"{realm}境 第{sub_level}重"

    embed = discord.Embed(title=f"{user.display_name} 的修煉狀態", color=0x87CEEB)
    embed.add_field(name="金錢", value=f"{player.get('money',0)} 元", inline=False)

    if player.get("direction") == "煉氣":
        embed.add_field(
            name="靈氣（煉氣）",
            value=f"{create_status_bar(qi, max_qi, '34')}\n{realm_text('煉氣', player.get('level_index',0), player.get('sub_level',1))}",
            inline=False
        )
    elif player.get("direction") == "煉體":
        embed.add_field(
            name="煉血（煉體）",
            value=f"{create_status_bar(blood, max_blood, '31')}\n{realm_text('煉體', player.get('level_index',0), player.get('sub_level',1))}",
            inline=False
        )
    else:
        embed.add_field(name="境界", value="尚未選擇修煉方向", inline=False)

    return embed

# --- 重置角色 ---
def get_base_character():
    return {
        "qi": 0, "blood": 0,
        "max_qi": 100, "max_blood": 100,
        "direction": None,
        "level_index": 0,
        "sub_level": 1,
        "log": [],
        "inventory": {},
        "money": 50
    }

# ====== 面板建構器 ======
def build_panel_view(user_id, mode="修煉"):
    if mode == "商店":
        return ShopPanelView(user_id)  # 內部會抽 3 個商品
    else:
        return CultivationPanelView(user_id)

# ====== 下拉式選單（永遠顯示在底部 row=4）======
class ActionSelect(discord.ui.Select):
    def __init__(self, user_id):
        self.user_id = user_id
        options = [
            discord.SelectOption(label="修煉", description="進入修煉面板"),
            discord.SelectOption(label="商店", description="查看商店")
        ]
        super().__init__(placeholder="選擇你的行動...", min_values=1, max_values=1, options=options, row=4)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的面板！", ephemeral=True)
            return
        choice = self.values[0]
        if choice == "商店":
            view = build_panel_view(self.user_id, "商店")
            await interaction.response.edit_message(
                content=f"🛒 商店 - 你目前擁有 {players[self.user_id].get('money',0)} 元",
                embed=None,
                view=view
            )
        else:
            view = build_panel_view(self.user_id, "修煉")
            embed = build_status_embed(interaction.user, players[self.user_id])
            await interaction.response.edit_message(
                content="選擇你的行動：",
                embed=embed,
                view=view
            )

# ====== 修煉面板 ======
class CultivationPanelView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        # 下拉式選單固定在底部
        self.add_item(ActionSelect(user_id))

    def add_items_to_inventory(self, player, items):
        if "inventory" not in player or not isinstance(player["inventory"], dict):
            player["inventory"] = {}
        if not items:
            return
        # 彙總此次事件的道具數量
        count = {}
        for it in items:
            name = it["name"]
            count[name] = count.get(name, 0) + 1
            player["inventory"][name] = player["inventory"].get(name, 0) + 1
        # Log：顯示獲得的道具清單
        got = "，".join([f"{n} x{q}" for n, q in count.items()])
        players[self.user_id]["log"].append(f"🎁 獲得道具：{got}")

    async def check_breakthrough(self, interaction):
        player = players[self.user_id]
        if player["direction"] == "煉氣" and player["qi"] >= player["max_qi"]:
            player["qi"] = 0
            player["sub_level"] += 1
        elif player["direction"] == "煉體" and player["blood"] >= player["max_blood"]:
            player["blood"] = 0
            player["sub_level"] += 1

        if player["sub_level"] > 9:
            player["sub_level"] = 1
            player["level_index"] += 1
            player["max_qi"] += 50
            player["max_blood"] += 50
            player["log"].append("🎉 你突破到了更高的境界！")

        save_players()
        return build_status_embed(interaction.user, player)

    @discord.ui.button(label="閉關", style=discord.ButtonStyle.blurple, row=0)
    async def meditate(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉面板！", ephemeral=True)
            return
        player = players[self.user_id]
        if player.get("direction") is None:
            await interaction.response.send_message("請先選擇修煉方向。", ephemeral=True)
            return

        if player["direction"] == "煉氣":
            event = random.choice(qi_training_events)
            gain = event["effect"]["qi"]
            player["qi"] += gain
            player["log"].append(f"🧘 闔關（煉氣）：{event['text']}（氣值+{gain}）")
        else:
            event = random.choice(body_training_events)
            gain = event["effect"]["blood"]
            player["blood"] += gain
            player["log"].append(f"🧘 閉關（煉體）：{event['text']}（血量+{gain}）")

        # 金錢（只在不為 0 時紀錄）
        if event.get("money", 0):
            player["money"] = player.get("money", 0) + event["money"]
            player["log"].append(f"💰 {event['text']}（金錢+{event['money']}）")

        # 道具
        self.add_items_to_inventory(player, event.get("items", []))

        embed = await self.check_breakthrough(interaction)
        await interaction.response.edit_message(
            content=f"🧘 {interaction.user.mention} 閉關：\n- {event['text']}",
            embed=embed,
            view=self
        )

    @discord.ui.button(label="歷練", style=discord.ButtonStyle.green, row=0)
    async def expedition(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉面板！", ephemeral=True)
            return
        player = players[self.user_id]
        if player.get("direction") is None:
            await interaction.response.send_message("請先選擇修煉方向。", ephemeral=True)
            return

        if player["direction"] == "煉氣":
            event = random.choice(qi_expedition_events)
            gain = event["effect"]["qi"]
            player["qi"] += gain
            player["log"].append(f"🌄 歷練（煉氣）：{event['text']}（氣值+{gain}）")
        else:
            event = random.choice(body_expedition_events)
            gain = event["effect"]["blood"]
            player["blood"] += gain
            player["log"].append(f"🌄 歷練（煉體）：{event['text']}（血量+{gain}）")

        if event.get("money", 0):
            player["money"] = player.get("money", 0) + event["money"]
            player["log"].append(f"💰 {event['text']}（金錢+{event['money']}）")

        self.add_items_to_inventory(player, event.get("items", []))

        embed = await self.check_breakthrough(interaction)
        await interaction.response.edit_message(
            content=f"🌄 {interaction.user.mention} 歷練：\n- {event['text']}",
            embed=embed,
            view=self
        )

    @discord.ui.button(label="查看狀態", style=discord.ButtonStyle.gray, row=1)
    async def status_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉面板！", ephemeral=True)
            return
        embed = build_status_embed(interaction.user, players[self.user_id])
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="查看事件記錄", style=discord.ButtonStyle.secondary, row=1)
    async def show_log(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉面板！", ephemeral=True)
            return
        log = players[self.user_id].get("log", [])
        if not log:
            await interaction.response.send_message("📜 目前還沒有任何事件。", ephemeral=True)
            return
        log_text = "\n".join(log[-20:])
        await interaction.response.send_message(f"📜 最近事件紀錄：\n{log_text}", ephemeral=True)

    @discord.ui.button(label="查看背包", style=discord.ButtonStyle.secondary, row=1)
    async def show_inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的背包！", ephemeral=True)
            return
        player = players[self.user_id]
        inv = player.get("inventory", {})
        if not inv:
            inv_text = "你的背包目前是空的。"
        else:
            inv_text = "📦 背包：\n" + "\n".join([f"🔹 {item} x{qty}" for item, qty in inv.items()])
        await interaction.response.send_message(inv_text, ephemeral=True)

# ====== 商店面板 ======
class ShopButton(discord.ui.Button):
    def __init__(self, user_id, item, shop_list):
        super().__init__(label=f"{item['name']} ({item['price']} 元)", style=discord.ButtonStyle.green, row=0)
        self.user_id = user_id
        self.item = item
        self.shop_list = shop_list

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的商店！", ephemeral=True)
            return
        player = players[self.user_id]
        if player.get("money", 0) < self.item["price"]:
            await interaction.response.send_message("💸 金幣不足，無法購買！", ephemeral=True)
            return

        # 購買
        player["money"] -= self.item["price"]
        if "inventory" not in player or not isinstance(player["inventory"], dict):
            player["inventory"] = {}
        player["inventory"][self.item["name"]] = player["inventory"].get(self.item["name"], 0) + 1
        player["log"].append(f"🛒 購買 {self.item['name']} -{self.item['price']} 元")
        save_players()

        # 更新商店面板（保持同一批商品）
        view = ShopPanelView(self.user_id, self.shop_list)
        await interaction.response.edit_message(
            content=f"🛒 商店 - 你目前擁有 {player.get('money',0)} 元",
            embed=None,
            view=view
        )

class ShopPanelView(discord.ui.View):
    def __init__(self, user_id, shop_list=None):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.shop_list = shop_list or random.sample(shop_items, 3)
        for it in self.shop_list:
            self.add_item(ShopButton(user_id, it, self.shop_list))
        # 下拉式選單固定在底部
        self.add_item(ActionSelect(user_id))

# --- 選擇方向 ---
class DirectionView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id

    @discord.ui.button(label="煉體", style=discord.ButtonStyle.red)
    async def power(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉選項！", ephemeral=True)
            return
        await start_cultivation(interaction, "煉體")

    @discord.ui.button(label="煉氣", style=discord.ButtonStyle.blurple)
    async def mana(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的修煉選項！", ephemeral=True)
            return
        await start_cultivation(interaction, "煉氣")

# --- 開始修煉 ---
async def start_cultivation(interaction, direction):
    user_id = interaction.user.id
    if user_id not in players:
        players[user_id] = get_base_character()
    players[user_id]["direction"] = direction
    # 確保新欄位存在（兼容舊存檔）
    players[user_id].setdefault("inventory", {})
    players[user_id].setdefault("money", 50)
    save_players()
    description = f"你選擇了 {direction} 修煉，一開始只能專注這個方向，將來可選擇雙修。"
    embed = build_status_embed(interaction.user, players[user_id])
    await interaction.response.edit_message(
        content=f"🎮 {interaction.user.mention} {description}\n選擇你的行動：",
        embed=embed,
        view=CultivationPanelView(user_id)
    )

# --- 靈根抽取 ---
def choose_root():
    rand = random.random()
    cumulative = 0
    for level, prob in talent_level.items():
        cumulative += prob
        if rand <= cumulative:
            root_level = level
            break
    rand = random.random()
    cumulative = 0
    for element, prob in talent.items():
        cumulative += prob
        if rand <= cumulative:
            root_type = element
            break
    return f"{root_level}{root_type}"

# --- Bot 事件 ---
@bot.event
async def on_ready():
    load_players()
    print(f"已登入為 {bot.user}")
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("光曆69年，您作為一位修真者來到了這世間。在這弱肉強食的亂世之中，您修練的每一動都將與您未來的生死息息相關...")
        await channel.send("輸入!start以開始遊戲..")

# --- 指令 ---
@bot.command()
async def start(ctx):
    user_id = ctx.author.id
    if user_id in players and players[user_id].get("direction") is not None:
        await ctx.send("你已經開始修煉了！")
        return
    if user_id not in players:
        players[user_id] = get_base_character()
        save_players()

    root = choose_root()
    players[user_id]["log"].append(f"抽到了靈根：{root}")
    save_players()

    intro_text = (
        f"🎮 {ctx.author.mention}\n"
        "現在你需要選擇修煉方向：\n"
        "- 煉體：強化自身肉身與力量\n"
        "- 煉氣：提升內力與法力\n"
        "**注意：一開始只能專注一個方向，將來有機會雙修。**"
    )
    await ctx.send(f"🎉 你這一世的資質為：{root}")
    await ctx.send(intro_text, view=DirectionView(user_id))

@bot.command()
async def status(ctx):
    user_id = ctx.author.id
    if user_id not in players:
        await ctx.send("你還沒有開始修煉，請輸入 `!start`")
        return
    if players[user_id].get("direction") is None:
        await ctx.send("你尚未選擇修煉方向，請先使用上方按鈕選擇。")
        return
    embed = build_status_embed(ctx.author, players[user_id])
    await ctx.send(embed=embed, view=CultivationPanelView(user_id))

@bot.command()
async def reset(ctx):
    user_id = ctx.author.id
    players[user_id] = get_base_character()
    save_players()
    await ctx.send(f"{ctx.author.mention} 你的角色已重置！")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, limit: int = 100):
    deleted = await ctx.channel.purge(limit=limit)
    await ctx.send(f"✅ 已刪除 {len(deleted)} 則訊息", delete_after=5)

# ===== 啟動 =====
bot.run(TOKEN)