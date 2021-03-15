import discord
import os
import sys
import json
from discord import message
import util
import guildClass
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
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

        if not started or message.author == self.user:
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
        \reset
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
        elif keyWords[0] == '\\reset':
            started = False
            await message.channel.send("Restarting...")
            try:
                os.remove(self.joinQ([str(message.guild.id) + '.json']))
            except:
                pass
            await self.on_ready()
            await message.channel.send("Restarted")
        elif keyWords[0] == '\\end':
            await self.terminate()
        elif keyWords[0] == '\\debug':
            self.debug(message)
        else:
            await message.channel.send(f"Did not recognize command '{keyWords[0]}'\nUse \\help to see a list of all possible commands")

    def debug(self, m):
        ci = self.guildInfo[m.guild.id].channelInfo
        for (channel, info) in ci.items():
            total = 0
            for day in info["content"].values():
                total += len(day)
            print(f"{channel.name} : {total}")

    async def history(self, m, keyWords):
        if len(keyWords) < 3:
            await m.channel.send("Incorrect number of arguments recieved")
            return
        
        userToCheck = 0
        channelsToCheck = []
        startTime = 0
        endTime = util.dtScore(datetime.datetime.now())

        # get user
        try:
            if keyWords[1] != "all":
                userToCheck = m.mentions[0].id
        except:
            m.channel.send(f'Did not recognize user "{keyWords[1]}"')
            return

        # get channel
        if keyWords[2] == "all":
            channelsToCheck = list(self.guildInfo[m.guild.id].channelInfo.keys())
        else:
            channelsToCheck = [m.channel_mentions[0]]
            if channelsToCheck[0] not in self.guildInfo[m.guild.id].channelInfo:
                await m.channel.send("Invalid channel recieved (might not exist or does not contain any messages)")
                return

        # get start time
        try:
            if len(keyWords) > 3 and keyWords[3] != "0":
                startTime = util.dtScore(util.inputToDTScore(keyWords[3]))
        except:
            m.channel.send(f'Did not recognize date "{keyWords[3]}"')
            return

        # get end time
        try:
            if len(keyWords) > 4 and keyWords[4] != "0":
                endTime = util.dtScore(util.inputToDTScore(keyWords[4]))
        except:
            m.channel.send(f'Did not recognize date "{keyWords[4]}"')

        if (endTime < started):
            await m.channel.send("Recived end time was less then start time")
            return
        
        # get sort
        sort = "messages"
        try:
            if len(keyWords) > 5:
                if keyWords[5] in ["messages", "phrase", "pins", "users"]:
                    sort = keyWords[5]

                    # if given a phrase, a format must also be given
                    if sort == "phrase":
                        try:
                            if keyWords[6] in ["noncap", "default", 'discord', 'noncapdiscord']:
                                frmat = keyWords[6]
                            else:
                                m.channel.send(f'Did not recognize format "{keyWords[6]}"')
                                return
                        except:
                            m.channel.send(f'Did not recieve format')
                            return

                        phrase = keyWords[7]
                        if len(keyWords) >= 8:
                            for continuedPhrase in m.content.split(' ')[8:]:
                                phrase += ' ' + continuedPhrase
        except:
            m.channel.send(f'Did not recognize sort "{keyWords[5]}"')
            return

        await m.channel.send("Gathering data...")
        ci = self.guildInfo[m.guild.id].channelInfo
        info = dict()
        for c in channelsToCheck:
            st = startTime if startTime != 0 else util.dtScore(c.created_at)
            for day in range(st, endTime + 1):
                if not util.isValidDTScore(day):
                    continue

                if day in ci[c]["content"].keys():
                    messages = ci[c]["content"][day]
                    if day == 0:
                        continue

                    if day not in info:
                        info[day] = 0

                    # messages
                    if sort == "messages":
                        # sort through messages
                        if keyWords[1] == "all":
                            # minor opt, just get len of all messages since we count them all
                            info[day] += len(messages)
                        else:
                            # loop through all messages, check if the sender is correct
                            for message in messages:
                                if message["author"] == userToCheck:
                                    info[day] += 1
                    elif sort == "phrase":
                        pass
                    elif sort == "pins":
                        pass
                    else:
                        pass


                else:
                    if day not in info:
                        info[day] = 0

        
        names = [mdt.date2num(util.cleanUTC(t)) for t in info.keys()]
        values = list(info.values())

        dateForm = mdt.DateFormatter("%m-%y")
        fig, ax = plt.subplots(figsize = (18, 18))

        ax.bar(names, values)
        ax.set(xlabel = "Date", ylabel = "Messages Sent (month - year)")
        ax.xaxis.set_major_formatter(dateForm)

        plt.savefig(str(m.guild.id) + '-history.png', bbox_inches = 'tight')
        plt.close()

        file = discord.File(str(m.guild.id) + '-history.png', filename = 'data.png')
        await m.channel.send(file = file)

        os.remove(str(m.guild.id) + '-history.png')

    async def help(self, m, keyWords):
        answers = {
            "default" : "To use \\help, type \\help {*command*}.\nCommands: history, ratio, reset, end, overview",
            "history" : "Generates a graph of the specified data.\nUsage: \\history user channel startTime endTime\n    User: Can be a specific @ or all. **Non-optional**.\n    Channel: Can be a specific # or all. **Non-optional**.\n    StartTime: A time in the format dd-mm-yyyy. **Optional**, defaults to creation of channel.\n    EndTime: A time in the format dd-mm-yyyy. **Optional**, defaults to current time, or use 0.\n    Sort: Tells the bot what data to draw from. Use \\help sort to see possible commands. **Optional**, defaults to messages, or use 0.",
            "ratio" : "Finds the amount of times a phrase was said, and the users that said it. Resulting data may not add up to 100%.\nUsage: \\ratio channel format phrase\n    Channel: Can be a specific # or all. **Non-optional**.\n    Format: Can be default, nonCap, discord, or nonCapDiscord. Tells the program how to determine if a phrase is within a message. **Non-optional**.\n       - Default: Naively searches for a phrase. Is case-sensitive, and will include the result if it is found within another word.\n       - NonCap: Similar to default, however it is case-insensitive.\n       - Discord: Attempts to match the search to result discord provides in their search bar. Is case-sensetive.\n       - NonCapDiscord: Similar to discord, however it is case-insensitive.\n    Phrase: No particular format, but cannot contain a backslash. **Non-optional**.",
            "reset" : "Restarts the bot, and also deletes all corresponding guild information.\nUsage: \\reset",
            "end" : "Terminates the bot.\nUsage: \\end",
            "overview" : r'''This bot was created to see more data about a specifc server. It is not 100% loss proof (funky stuff happens when deleting messages). To see the source code, see https://github.com/Andallfor/infoBot.'''
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
        for message in g.channelInfo["content"][util.dtScore(m.created_at)]:
            if message.id == m.id:
                g.channelInfo["content"][util.dtScore(m.created_at)].pop(i)
            i += 1

    async def ratio(self, m, keyWords):
        # make sure its in the right format
        if len(keyWords) <= 2:
            await m.channel.send("Incorrect number of arguments recieved")
            return

        await m.channel.send("Gathering data...")

        if keyWords[2] in ["default", "noncap", "discord", "noncapdiscord"]:
            frmat = keyWords[2]
        else:
            await m.channel.send(f'Unable to read given format "{keyWords[2]}"')
            return

        phrase = keyWords[3]
        if len(keyWords) >= 4:
            for continuedPhrase in m.content.split(' ')[4:]:
                phrase += ' ' + continuedPhrase
        
        users = dict()
        total = 0

        if keyWords[1].lower() == "all":
            # search for phrase in all channels
            channelsToSearch = m.guild.text_channels

            for c in channelsToSearch:
                _u, _t = self.singleChannelSearch(phrase, self.guildInfo[m.guild.id].channelInfo[c], frmat)
                for (key, value) in _u.items():
                    if key in users:
                        users[key] += value
                    else:
                        users[key] = value
                total += _t
        else:
            # search for phrase in single channel
            if len(m.channel_mentions) != 1:
                await m.channel.send("Unable to parse given channels")
            users, total = self.singleChannelSearch(phrase, self.guildInfo[m.guild.id][m.channel_mentions[0].id], frmat)
            
        messageToSend = f'Found "{phrase}" a total of {total} times.\n'

        sortedUsers = sorted(users, key = users.get, reverse = True)

        names = sortedUsers[:min(len(sortedUsers), 10)]
        values = [users[user] for user in names]
        names = ["Unknown" if self.get_user(user) == None else self.get_user(user).display_name for user in names]

        fig = plt.figure(figsize = (9, 9))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('equal')

        p, tx, autotexts = ax.pie(values, labels = names, autopct = '%1.2f%%')

        for i, a in enumerate(autotexts):
            a.set_text(f'{values[i]} ({round(values[i] / total, 2) * 100}%)')

        plt.savefig(str(m.guild.id) + '-pie.png', bbox_inches = 'tight')
        plt.close()

        file = discord.File(str(m.guild.id) + '-pie.png', filename = 'data.png')
        await m.channel.send(messageToSend, file = file)

        os.remove(str(m.guild.id) + '-pie.png')

    def singleChannelSearch(self, phrase, ci, frmat):
        users = dict()
        total = 0

        for day in ci["content"].values():
            for message in day:
                # dont count self references
                if message["author"] == self.user.id:
                    continue

                contains = util.getFormat(frmat, phrase, message["content"])

                if contains:
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