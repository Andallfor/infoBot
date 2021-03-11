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

        started = True
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

        if not started or message.author == self.user or len(message.content) == 0:
            return

        # save msg
        await self.guildInfo[message.guild.id].newMsg(message.channel, message)

        # command to run bot is \
        if message.content[0] != "\\":
            return
        
        '''
        Avaliable commands:
        \help
        \history user channel startTime endTime sort
            user, channel can be all
            startTime, endTime can be default
            sort can be totalMessages, and userChange
        \ratio channel phrase
        \init
        \end
        '''

        keyWords = message.content.split(' ')
        keyWords = [i.lower() for i in keyWords]

        if keyWords[0] == '\\help':
            pass
        elif keyWords[0] == '\\history':
            pass
        elif keyWords[0] == '\\ratio':
            print("recieved command")
            await self.ratio(message, keyWords)
        elif keyWords[0] == '\\init':
            started = False
            await message.channel.send("Restarting...")
            await self.on_ready()
            await message.channel.send("Restarted")
        elif keyWords[0] == '\\end':
            await self.terminate()
        else:
            await message.channel.send(f"Did not recognize command '{keyWords[0]}'\nUse \\help to see a list of all possible commands")
    
    async def ratio(self, m, keyWords):
        # make sure its in the right format
        if len(keyWords) <= 2:
            await m.channel.send("Incorrect number of arguments recieved")
            return

        phrase = ' '.join(keyWords[2:])
        users = dict()
        total = 0
        g = self.guildInfo[m.guild.id]

        if keyWords[1].lower() == "all":
            # search for phrase in all channels
            channelsToSearch = m.guild.text_channels

            for c in channelsToSearch:
                _u, _t = self.singleChannelSearch(phrase, g, c)
                users.update(_u)
                total += _t
        else:
            # search for phrase in single channel
            if len(m.channel_mentions) != 1:
                await m.channel.send("Unable to parse given channels")
            users, total = self.singleChannelSearch(phrase, self.guildInfo[m.guild.id], m.channel_mentions[0])
            
        await m.channel.send(f'Found "{phrase}" a total of {total} times.')
        for (user, times) in users.items():
            u = self.get_user(int(user))
            u = "Unknown" if u == None else u.display_name
            await m.channel.send(f"{u}: {times} ({round((times/total) * 100, 2)}%)")
    
    def singleChannelSearch(self, phrase, g, c):
        users = dict()
        total = 0

        for day in g.channelInfo[c]["content"].values():
            for message in day:
                if phrase in message["content"]:
                    # dont count self references
                    if message["author"] == self.user.id:
                        continue

                    if message["author"] not in users:
                        users[message["author"]] = 0
                    users[message["author"]] += 1
                    total += 1
        
        return (users, total)

    def joinQ(self, msgs):
        s = "guilds"
        for m in msgs:
            s += os.sep + str(m)
        return s

intents = discord.Intents.default()
intents.members = True
client = _client(intents = intents)

if (len(sys.argv) != 2):
    sys.exit("Incorrect Usage. Input token along with command.")

token = sys.argv[1]
client.run(token)