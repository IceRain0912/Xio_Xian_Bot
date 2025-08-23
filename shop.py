# shop.py
import random
import discord
from items import shop_items

class ShopButton(discord.ui.Button):
    def __init__(self, user_id, item, shop_list):
        super().__init__(label=f"{item['name']} ({item['price']} 元)", style=discord.ButtonStyle.green, row=0)
        self.user_id = user_id
        self.item = item
        self.shop_list = shop_list

    async def callback(self, interaction: discord.Interaction):
        from game import players  # 延遲 import 避免循環
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ 這不是你的商店！", ephemeral=True)
            return
        player = players[self.user_id]
        if player.get("money", 0) < self.item["price"]:
            await interaction.response.send_message("💸 金幣不足，無法購買！", ephemeral=True)
            return
        # 購買
        player["money"] -= self.item["price"]
        player["inventory"][self.item["name"]] = player["inventory"].get(self.item["name"], 0) + 1
        player["log"].append(f"🛒 購買 {self.item['name']} -{self.item['price']} 元")
        from game import save_players
        save_players()
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
