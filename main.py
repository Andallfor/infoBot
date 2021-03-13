import discord
import os
import sys
import json

from discord.embeds import Embed
import guildClass
import matplotlib.pyplot as plt
import datetime
import io

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
        \history user channel startTime endTime
            user, channel can be all
            startTime, endTime can be default
        \ratio channel phrase
        \init
        \end
        '''

        keyWords = message.content.split(' ')
        keyWords = [i.lower() for i in keyWords]

        if keyWords[0] == '\\help':
            await self.help(message, keyWords)
        elif keyWords[0] == '\\history':
            await self.history(message, keyWords)
        elif keyWords[0] == '\\ratio':
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

    async def history(self, m, keyWords):
        if len(keyWords) < 3 and len(keyWords) <= 5:
            await m.channel.send("Incorrect number of arguments recieved")
            return
        
        userToCheck = 0
        channelsToCheck = []
        startTime = 0
        endTime = self.dtScore(datetime.datetime.now())

        # get user
        if keyWords[1] != "all":
            userToCheck = m.mentions[0].id

        # get channel
        if keyWords[2] == "all":
            channelsToCheck = list(self.guildInfo[m.guild.id].channelInfo.keys())
        else:
            channelsToCheck = [m.channel_mentions[0]]
            if channelsToCheck[0] not in self.guildInfo[m.guild.id].channelInfo:
                await m.channel.send("Invalid channel recieved (might not exist or does not contain any messages)")
                return

        # get start time
        if len(keyWords) >= 4 and keyWords[4] != "0":
            startTime = self.inputToDTScore(keyWords[4])

        # get end time
        if len(keyWords) == 5 and keyWords[5] != "0":
            endTime = self.inputToDTScore(keyWords[5])
        
        if (endTime < started):
            await m.channel.send("Recived end time was less then start time")
            return
        
        await m.channel.send("Gathering data...")
        ci = self.guildInfo[m.guild.id].channelInfo
        info = dict()
        for c in channelsToCheck:
            st = startTime if startTime != 0 else self.dtScore(c.created_at)
            for day in range(st, endTime + 1):
                if not self.isValidDTScore(day):
                    continue

                if day in ci[c]["content"].keys():
                    messages = ci[c]["content"][day]
                    if day == 0:
                        continue

                    if day not in info:
                        info[day] = 0
                
                    # sort through messages
                    if keyWords[1] == "all":
                        # minor opt, just get len of all messages since we count them all
                        info[day] += len(messages)
                    else:
                        # loop through all messages, check if the sender is correct
                        if keyWords[2] != 'all':
                            info[day] += 1
                        else:
                            for message in messages:
                                if message["author"] == userToCheck:
                                    info[day] += 1
                else:
                    if day not in info:
                        info[day] = 0

        if len(info) < 25:
            names = [str(self.cleanUTC(t)) for t in info.keys()]
        else:
            names = [i for i in range(len(info))]
        values = list(info.values())

        plt.figure(1, figsize=(12, 6))

        plt.subplot(131)
        plt.subplots_adjust(right = 3)
        plt.scatter(names, values)
        plt.suptitle('Data')

        plt.savefig(str(m.guild.id) + '.png', bbox_inches = 'tight')
        plt.close()

        file = discord.File(str(m.guild.id) + '.png', filename = 'data.png')
        await m.channel.send(file = file)

        os.remove(str(m.guild.id) + '.png')
    
    def inputToDTScore(self, phrase):
        parts = phrase.split('-')
        return datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]))
    
    def strDT(self, dt):
        return f"{dt.day}/{dt.month}/{str(dt.year)[2:]}"
    
    def isValidDTScore(self, dtScore):
        # sue me
        try:
            self.cleanUTC(dtScore)
            return True
        except:
            return False

    async def help(self, m, keyWords):
        answers = {
            "default" : "To use \\help, type \\help {*command*}.\nCommands: history, ratio, init, end, overview, sort",
            "history" : "Generates a graph of the specified data.\nUsage: \\history user channel startTime endTime\n    User: Can be a specific @ or all. **Non-optional**.\n    Channel: Can be a specific # or all. **Non-optional**.\n    StartTime: A time in the format dd-mm-yyyy. **Optional**, defaults to creation of channel.\n    EndTime: A time in the format dd-mm-yyyy. **Optional**, defaults to current time, or use 0.\n    Sort: Tells the bot what data to draw from. Use \\help sort to see possible commands. **Optional**, defaults to messages, or use 0.",
            "ratio" : "Finds the amount of times a phrase was said, and the users that said it. Resulting data may not add up to 100%.\nUsage: \\ratio channel phrase\n    Channel: Can be a specific # or all. **Non-optional**.\n    Phrase: No particular format, but cannot contain the character '\\'. **Non-optional**",
            "init" : "Restarts the bot.\nUsage: \\init",
            "end" : "Terminates the bot.\nUsage: \\end",
            "sort" : "Not yet implemented",
            "overview" : r"This bot was created to see more data about a specifc server. It is not 100% loss proof (funky stuff happens when deleting messages).\nTo see the source code, see https://github.com/Andallfor/infoBot."
        }

        message = answers["default"]
        if len(keyWords) == 2 and keyWords[1].lower() in answers:
            message = answers[keyWords[1].lower()]
        
        await m.channel.send(message)
    
    async def on_message_delete(self, message):
        self.internalDelete(message)

    async def on_bulk_message_delete(self, messages):
        for message in messages:
            self.internalDelete(message)

    def internalDelete(self, m):
        g = self.guildInfo[m.guild.id]
        i = 0
        for message in g.channelInfo["content"][g.datetimeScore(m.created_at)]:
            if message.id == m.id:
                g.channelInfo["content"][g.datetimeScore(m.created_at)].pop(i)
            i += 1

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
        i = 0
        for (user, times) in users.items():
            u = self.get_user(int(user))
            u = "Unknown" if u == None else u.display_name
            await m.channel.send(f"{u}: {times} ({round((times/total) * 100, 2)}%)")
            i += times
        if i != total:
            await m.channel.send(f"Deleted messages: {total - i} ({round(((i - total)/total) * 100, 2)}%)")
    
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
    
    # should throw this into a seperate class
    def dtScore(self, dt):
        return int((dt.year * 10_000) + (dt.month * 100) + dt.day)

    def cleanUTC(self, score):
        return datetime.datetime(year = self.year(score), month = self.month(score), day = self.day(score))
    
    def year(self, score):
        return int(score / 10_000)
    
    def month(self, score):
        return int((score - (self.year(score) * 10_000)) / 100)
    
    def day(self, score):
        return int(score - ((self.year(score) * 10_000 ) + (self.month(score) * 100)))

intents = discord.Intents.default()
intents.members = True
client = _client(intents = intents)

if (len(sys.argv) != 2):
    sys.exit("Incorrect Usage. Input token along with command.")

token = sys.argv[1]
client.run(token)