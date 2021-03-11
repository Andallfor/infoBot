import discord
import os
import sys
import timeit
import json
import guildClass

started = False

class _client(discord.Client):
    async def on_ready(self):
        global started
        if started:
            return

        started = True

        # {guild.id : guild}
        self.guildInfo = dict()

        for g in self.guilds:
            gd = guildClass.guild()

            if os.path.exists(self.joinQ([str(g.id) + ".json"])):
                # already saved it, so just unload it
                gd.loadFromDir(g, self.joinQ([str(g.id) + ".json"]))
                await gd.checkForUpdates()
            else:
                await gd.manualInit(g)

            self.saveGuildClass(gd)
            self.guildInfo[g.id] = gd
        
        print("ready")

    async def terminate(self):
        # save files
        for (key, item) in self.guildInfo.items():
            self.saveGuildClass(item)
        
        await self.logout()
        sys.exit("Terminated bot")
    
    def saveGuildClass(self, guild):
        json.dump(self.toJson(guild.channelInfo), open(self.joinQ([str(guild.guild.id) + ".json"]), "w"), indent = 4)

    def toJson(self, d):
        rd = dict()
        for (key, value) in d.items():
            rd[int(key.id)] = value
        
        return rd
    
    async def on_message(self, message):
        global started

        if not started:
            return

        # save msg
        await self.guildInfo[message.guild.id].newMsg(message.channel, message)

        # command to run bot is \
        if len(message.content) == 0 or message.content[0] != "\\" or message.author == self.user:
            return
        
        '''
        Avaliable commands:
        \help
        \history user channel startTime endTime sort
            user, channel can be all
            startTime, endTime can be default
            sort can be totalMessages, and userChange
        \ratio phrase channel
        \init
        \default channel
        \end
        '''

        keyWords = message.content.split(' ')
        keyWords = [i.lower() for i in keyWords]

        if keyWords[0] == '\\help':
            pass
        elif keyWords[0] == '\\history':
            pass
        elif keyWords[0] == '\\ratio':
            if (len(keyWords) <= 2):
                await message.channel.send(f"Usage: \\ratio channel phrase")
            else:
                try:
                    c = self.get_channel(int(keyWords[1][2 : len(keyWords[1]) - 1]))
                except:
                    await message.channel.send("Invalid channel bitch")
                    return
                if (c == None):
                    await message.channel.send("Invalid channel bitch")
                else:
                    await self.ratio(' '.join(keyWords[2:]), c)
        elif keyWords[0] == '\\init':
            started = False
            await self.on_ready()
        elif keyWords[0] == '\\end':
            await self.terminate()
        else:
            await message.channel.send(f"Did not recognize command '{keyWords[0]}'\nUse \\help to see a list of all possible commands")
    
    async def ratio(self, phrase, channel):
        initT = timeit.default_timer()
        lst = channel.history(limit = 5000).get(author_name = "Andallfor")
        endT = timeit.default_timer()

        #await channel.send(f"Indexed {len(lst)} messages in {endT - initT}")
        await channel.send(lst)

    def joinQ(self, msgs):
        s = "guilds"
        for m in msgs:
            s += os.sep + str(m)
        return s

client = _client()

if (len(sys.argv) != 2):
    sys.exit("Incorrect Usage. Input token along with command.")

token = sys.argv[1]
client.run(token)