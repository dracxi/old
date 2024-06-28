import discord
from discord import commands
from utils.HelpCommand import HelpEmbed

optionss = [
  discord.SelectOption(label="Main Menu",
                       value="main",
                       description="Bot Information and links"),
  discord.SelectOption(label="Fun", value="Fun", description="Fun commands"),
  discord.SelectOption(label="Interactions",
                       value="Interactions",
                       description="Under Development , Prefix is `Miko`"),
  discord.SelectOption(label="Zay", value="Zay", description="Zervo commands")
]


class HelpView(discord.ui.View):

  def __init__(self, bot, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.bot = bot
    self.helpembed = HelpEmbed(bot)
    options = [
      discord.SelectOption(label=info['cog'], description=info['cmds'][:99])
      for info in self.helpembed.Help_list()
    ]
    self.select = (discord.ui.Select(placeholder="Select a option",
                                     min_values=1,
                                     max_values=1,
                                     options=options))
    self.add_item(self.select)
    self.select.callback = self.on_select

  async def on_timeout(self):
    self.disable_all_items()
    await self.message.edit(content="", view=self)

  async def on_select(self, interaction: discord.Interaction):
    select = self.select
    cog = select.values[0]
    if cog == "Main Manu":
      embed = await self.helpembed.HelpMain()
    else:
      embed = await self.helpembed.Help_cog(cog)
    await interaction.response.edit_message(embed=embed)
