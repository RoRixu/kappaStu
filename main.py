import discord
import asyncio
import os
import time
from discord import app_commands, FFmpegPCMAudio
from discord.ext import commands
from config import config



class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.presences = True
        intents.voice_states = True
        self.voicechannel = None
        super().__init__(command_prefix=commands.when_mentioned_or('&'), intents=intents,application_id=config.APP_ID)

    async def setup_hook(self):
        await self.load_extension(f'cogs.Voice.voicecommands')
        await self.load_extension(f'cogs.MiniGames.miniGames')
        await self.tree.sync(guild=discord.Object(id=config.GUILD))
        await self.tree.sync()
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        for guild in self.guilds:
            print("Joined {guild}".format(guild=guild.name))
    async def on_voice_state_update(self,member,before,after):
        userswithfanfare = os.listdir(config.AUDIO_DIR + "/onchannelenter")
        for i in range(len(userswithfanfare)):
            userswithfanfare[i] = userswithfanfare[i][:-4]
            if userswithfanfare[i][-1] == "0":
                userswithfanfare.remove(userswithfanfare[i])
            elif userswithfanfare[i][-1] == "1":
                userswithfanfare[i] = userswithfanfare[i][:-1]
        if member.name in userswithfanfare and after.channel is not None and before.channel != after.channel:
            channel = member.voice.channel
            if self.voicechannel not in self.voice_clients:
                self.voicechannel = await channel.connect()
            if self.voicechannel.channel != channel:
                await self.voicechannel.disconnect()
                self.voicechannel = await channel.connect()
            source = FFmpegPCMAudio(config.AUDIO_DIR + "/onchannelenter/"+member.name+"1.mp3")
            self.voicechannel.play(source)
            while self.voicechannel.is_playing():
                time.sleep(1)
        if self.voicechannel is not None:
            numberofusers = 0
            for member in self.voicechannel.channel.members:
                if not member.bot:
                    numberofusers = numberofusers + 1
            if numberofusers == 0:
                await self.voicechannel.disconnect()


client = Bot()
async def start():
    async with client:
        client.tree.copy_global_to(guild=discord.Object(id=config.GUILD))
        await client.start(config.TOKEN)
asyncio.run(start())