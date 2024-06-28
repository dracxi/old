import discord


class HelpEmbed():

  def __init__(self, bot):
    self.bot = bot

  async def HelpMain(self):
    embed = discord.Embed(
      description=
      f"Welcome in {self.bot.user.mention}'s help, you will find here all the available commands"
    )
    embed.add_field(
      name="Info",
      value=
      f"{self.bot.user.mention} is a unoffcial zervo bot developed by @.dracx")
    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
    return embed

  async def Help_cog(self, cog):
    cogs = self.bot.get_cog(cog)
    embed = discord.Embed(title=f"Viewing {cogs.__cog_name__} Category",
                          description=cogs.description)
    command_list = []
    for cmd in cogs.get_commands():
      if isinstance(cmd, discord.SlashCommand):
        prefix = "/"
      else:
        prefix = self.bot.command_prefix
      command_list.append(f"`{prefix}`**{cmd}**: {cmd.description}")
    embed.add_field(name="Commands",
                    value=f"".join([f"{x}\n" for x in command_list]))
    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar)
    return embed

  async def Help_command(self, com):
    cmd = None
    for cogs in self.bot.cogs:
      cog = self.bot.get_cog(cogs)
      for cmds in cog.get_commands():
        if cmds.name == com:
          cmd = cmds
          break

    try:

      if cmd is None:
        embed = await HelpEmbed.HelpMain(self)
      else:
        if isinstance(cmd, discord.SlashCommand):
          prefix = "/"
        else:
          prefix = self.bot.command_prefix
        embed = discord.Embed(title=f"Viewing {cmd} command",
                              description=f"{prefix}{cmd} : {cmd.description}")
        embed.set_author(name=self.bot.user.name,
                         icon_url=self.bot.user.avatar)

    except Exception as e:
      print(e)
      embed = None

    return embed

  def Help_list(self):
    help_list = [{'cog': 'Main Manu', 'cmds': 'Main Menu'}]
    cmd_list = []
    for cogs in self.bot.cogs:
      cog = self.bot.get_cog(cogs)
      for cmd in cog.get_commands():
        cmd_list.append(cmd)
      cmds = ''.join([f'{x}, ' for x in cmd_list])
      help_list.append({'cog': cog.__cog_name__, 'cmds': cmds})
      cmd_list = []
    return help_list
