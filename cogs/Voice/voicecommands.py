import time
import random
import discord
import os
from typing import List
from config import config
from discord import FFmpegPCMAudio, app_commands, ui
from discord.ext import commands


async def play(self, interaction: discord.Interaction, clip):
    channel = interaction.user.voice.channel
    if channel != None:
        if self.bot.voicechannel not in self.bot.voice_clients:
            self.bot.voicechannel = await channel.connect()
        if self.bot.voicechannel.channel != channel:
            await self.bot.voicechannel.disconnect()
            self.bot.voicechannel = await channel.connect()
        source = FFmpegPCMAudio(clip)
        self.bot.voicechannel.play(source)
    else:
        await interaction.response.send_message(interaction.user.name + " is not in a channel.")

class stuSelect(discord.ui.Select):
    def __init__(self,bot,clipdir):
        self.clipdir=clipdir
        self.bot = bot
        options = []
        clipList = os.listdir(self.clipdir)
        for i in range(len(clipList)):
            options.append(discord.SelectOption(label=str(clipList[i][:-4])))
        super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await play(self, interaction, self.clipdir+"/"+self.values[0]+".mp3")
        returnstr = self.values[0]+" played"
        await interaction.response.edit_message(content=returnstr,view=None)

class stuSelectView(discord.ui.View):
    def __init__(self, bot,clipdir):
        self.bot=bot
        self.clipdir = clipdir
        super().__init__(timeout=60)
        self.add_item(stuSelect(self.bot, self.clipdir))

class VoiceCommands(commands.Cog):
    def __init__(self, bot: commands.Bot)->None:
        self.bot = bot

    def isStu(interaction: discord.Interaction) -> bool:
        return interaction.user.id == config.STU_ID


    @app_commands.command(name="clip",description="Plays a clip in channel user is in.")
    @app_commands.describe(clip="Name of the clip to play.")
    async def clip(self,interaction: discord.Interaction,clip:str)->None:
        clipdir = config.AUDIO_DIR+"/voice/"+clip
        if os.path.isdir(clipdir):
            randomClip = random.randint(1, len(os.listdir(clipdir)))
            clipdir = clipdir + "/" + clip + str(randomClip) + ".mp3"
        else:
            clipdir = clipdir + ".mp3"
        await play(self,interaction,clipdir)
        await interaction.response.send_message(clip+" played.",ephemeral=True)

    @clip.autocomplete("clip")
    async def clipAutocomplete(self,interaction: discord.Interaction, current:str) -> List[app_commands.Choice[str]]:
        clipList = os.listdir(config.AUDIO_DIR+"/voice")
        for i in range(len(clipList)):
            if os.path.isfile(config.AUDIO_DIR+"/voice/"+clipList[i]):
                clipList[i] = clipList[i][:-4]
        return [app_commands.Choice(name=clip,value=clip)
                for clip in clipList if current.lower() in clip.lower()
                ]

    @app_commands.command(name="stuclip",description="Plays a stu clip.")
    @app_commands.describe(
        type = "The type of clip to play."
    )
    @app_commands.check(isStu)
    async def stuClip(self,interaction: discord.Interaction, type:str):
        clipdir = config.AUDIO_DIR + "/stu/" +type
        await interaction.response.send_message("Which clip to play?",view=stuSelectView(clipdir=clipdir,bot=self.bot),
                                                ephemeral=True)
    @stuClip.autocomplete("type")
    async def typeAutocomplete(self,interaction: discord.Interaction, current:str) -> List[app_commands.Choice[str]]:
        typeList = os.listdir(config.AUDIO_DIR+"/stu")
        return [app_commands.Choice(name=type,value=type)
                for type in typeList if current.lower() in type.lower()
                ]

    @app_commands.command(name="togglefanfare",description="Toggle whether or not your fanfare plays when you join a channel")
    async def togglefanfare(self,interaction: discord.Interaction):
        clipList = os.listdir(config.AUDIO_DIR+"/onchannelenter")
        userNameLen = len(interaction.user.name)
        returnstr = "You do not have a fanfare."
        for i in range(len(clipList)):
            if clipList[i][0:userNameLen] == interaction.user.name:
                if clipList[i][-5] == "0":
                    os.rename(config.AUDIO_DIR+"/onchannelenter/"+clipList[i],
                              config.AUDIO_DIR+"/onchannelenter/"+interaction.user.name+"1.mp3")
                    returnstr = "Your fanfare is now enabled."
                elif clipList[i][-5] == "1":
                    os.rename(config.AUDIO_DIR+"/onchannelenter/"+clipList[i],
                              config.AUDIO_DIR+"/onchannelenter/"+interaction.user.name+"0.mp3")
                    returnstr = "Your fanfare is now disabled."
        await interaction.response.send_message(returnstr,ephemeral=True)






async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VoiceCommands(bot),guilds=[discord.Object(id=config.GUILD)])
