import discord
import os
import sys
import json
import util
import guildClass
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
import datetime

started = False

class _client(discord.Client):

   
    ######################################################
    # INIT/TERMINATION                                   #
    ######################################################
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
    
  
    ######################################################
    # MESSAGE CONTROL                                    #
    ######################################################
    async def on_message(self, message):
        global started

        if not started or message.author == self.user:
            return

        # save msg
        await self.guildInfo[message.guild.id].newMsg(message.channel, message)

        # command to run bot is \
        if len(message.content) > 0 and message.content[0] != "\\":
            return

        keyWords = message.content.split(' ')
        keyWords = [i.lower() for i in keyWords]

        if keyWords[0] == '\\help':
            await self.help(message, keyWords)
        elif keyWords[0] == '\\history':
            await self.history(message, keyWords)
        elif keyWords[0] == '\\ratio':
            await self.ratio(message, keyWords)
        elif keyWords[0] == '\\dratio':
            await self.dRatio(message, keyWords)
        elif keyWords[0] == '\\reset' and message.author.id == 425786074812383233:
            started = False
            await message.channel.send("Restarting...")
            try:
                os.remove(self.joinQ([str(message.guild.id) + '.json']))
            except:
                pass
            await self.on_ready()
            await message.channel.send("Restarted")
        elif keyWords[0] == '\\end' and message.author.id == 425786074812383233:
            await self.terminate()
        else:
            await message.channel.send(f"Did not recognize command '{keyWords[0]}'\nUse \\help to see a list of all possible commands")

    async def on_message_delete(self, message):
        self.internalDelete(message)

    async def on_bulk_message_delete(self, messages):
        for message in messages:
            self.internalDelete(message)

    def internalDelete(self, m):
        g = self.guildInfo[m.guild.id]
        i = 0
        for message in g.channelInfo[m.channel]["content"][util.dtScore(m.created_at)]:
            if message.id == m.id:
                g.channelInfo["content"][util.dtScore(m.created_at)].pop(i)
                return
            i += 1

    ######################################################
    # USER COMMANDS                                      #
    ######################################################
    async def history(self, m, keyWords):
        ######################################################
        # GET USER VALUES                                    #
        ######################################################
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
                if len(keyWords) > 5:
                    if keyWords[5] in ["uniqueusers", "users"]:
                        await m.channel.send('Detected sort "UniqueUsers". Setting users to "all".')
                        userToCheck = 0
                userToCheck = m.mentions[0].id
        except:
            m.channel.send(f'Did not recognize user "{keyWords[1]}"')
            return

        # get channel
        if keyWords[2] == "all":
            if len(keyWords) > 5:
                if keyWords[5] in ["uniqueusers", "users"]:
                    await m.channel.send(f'Detected sort "{keyWords[5]}". Channel must a specific channel, where join messages are sent.')
                    return
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
                if keyWords[5] in ["messages", "phrase", "pins", "users", "uniqueusers"]:
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
                else:
                    m.channel.send(f'Did not recognize sort "{keyWords[5]}"')
                    return    
        except:
            m.channel.send(f'Did not recognize sort "{keyWords[5]}"')
            return

        ######################################################
        # GET DATA                                           #
        ######################################################

        await m.channel.send("Gathering data...")
        ci = self.guildInfo[m.guild.id].channelInfo
        info = dict()
        seen = [] # only used if sort == "uniqueuser"
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
                        for message in messages:
                            if util.getFormat(frmat, phrase, message["content"]):
                                info[day] += 1
                    elif sort == "pins":
                        for message in messages:
                            if message["type"][1] == 6:
                                info[day] += 1
                    elif sort == "uniqueusers":
                        for message in messages:
                            if message["author"] not in seen and self.get_user(message["author"]) != None:
                                seen.append(message["author"])
                        info[day] = int(len(seen))
                    else:
                        # user join (non-unique)
                        for message in messages:
                            if message["type"][1] == 7:
                                info[day] += 1
                else:
                    if day not in info:
                        info[day] = 0
                    if sort == "uniqueusers":
                        info[day] = int(len(seen))

        ######################################################
        # GENERATE PLOT                                      #
        ######################################################

        names = [mdt.date2num(util.cleanUTC(t)) for t in info.keys()]
        values = list(info.values())

        graph = "bar"
        if sort in ["uniqueusers"]:
            graph = "line"

        file = util.quickPlot((names, values), ("Date", "Data"), (26, 14), m.guild, "-history.png", graph, True)

        await m.channel.send(file = file)

    async def help(self, m, keyWords):
        answers = {
            "default" :     ("To use \\help, type \\help {*command*}.\n"
                             "Commands: history, ratio, overview, sort, format"),

            "history" :     ("Generates a graph of the specified data.\n"
                             "Usage: \\history user channel startTime endTime sort (format phrase)\n"
                             "     User: Can be a specific @ or all. **Non-optional**.\n"
                             "     Channel: Can be a specific # or all. **Non-optional**.\n"
                             "     StartTime: A time in the format dd-mm-yyyy. **Optional**, defaults to creation of channel.\n"
                             "     EndTime: A time in the format dd-mm-yyyy. **Optional**, defaults to current time, or use 0.\n"
                             "     Sort: Tells the bot what data to draw from. Use \\help sort to see possible commands. **Optional**, defaults to messages.\n"
                             '     Format: Use \\help format to see possible commands. **Only used if the sort is "phrase"**.\n'
                             '     Phrase: No particular format, but cannot contain a backslash. **Only used if the sort is "phrase"**.\n'),

            "ratio" :       ("Finds the amount of times a phrase was said, and the users that said it. Resulting data may not add up to 100%.\n"
                             "Usage: \\ratio channel format phrase\n"
                             "     Channel: Can be a specific # or all. **Non-optional**.\n"
                             "     Tells the program how to determine if a phrase is within a message. Use \\help format to see possible commands. **Non-optional**.\n"
                             "     Phrase: No particular format, but cannot contain a backslash. **Non-optional**."),
            
            "dratio":       ("A more specific form of \\ratio. Finds the ratio of specific elements instead of a phrase.\n"
                             "Usage: \\dRatio user dSort (format phrase)\n"
                             "     User can be a specific @ or all. **Non-optional**.\n"
                             "     dSort: Tells the bot what data to look for. See \\dSort. **Non-optional**."),

            "dsort":        ("Specifies what data that dRatio looks for.\n"
                             "     Pins: Looks for the total amount of pins. Requires user to be all.\n"
                             "     Phrase: Looks for the relationship between the times a user has said a certain phrase versus their total messages. Requies use of an additional format and phrase command, and user must be a @.\n"),

            "common":       ("Common: Looks for the 20 most common words a user/server has said.\n"
                             "Usage: \\common user format ignore customIgnore"
                             "     Format: See \\format. **Non-optional**.\n"
                             "     Ignore: Can be either ignoreCommon or ignoreCustom. **Non-optional**.\n"
                             "          ignoreCommon: Ignores the most common words. Still allows for additional custom ignores.\n"
                             "          ignoreCustom: Only ignores words that the user inputs.\n"
                             "     CustomIgnore: An input for words and phrases that will be ignored by the bot. Use hyphens to join words together. I.E. Ignore-This-Phrase. **Optional**."),

            "format" :      ("Specifies how to determine if a phrase is within another. Can be default, nonCap, discord, or nonCapDiscord.\n"
                             "     Default: Naively searches for a phrase. Is case-sensitive, and will include the result if it is found within another word.\n"
                             "     NonCap: Similar to default, however it is case-insensitive.\n"
                             "     Discord: Attempts to match the search to result discord provides in their search bar. Is case-sensetive.\n"
                             "     NonCapDiscord: Similar to discord, however it is case-insensitive.\n"),
            
            "sort" :        ("Specifies what data to draw from. Can be messages, phrase, pins, users and uniqueUsers.\n"
                             "     Phrase: Looks for a certain message. Requires the use of an additional format and phrase command.\n"
                             "     Pins: Looks for when pins were added. Does not require any other arguments.\n"
                             "     Users: Looks for when users were added to the server. Server must have messages sent upon arrival to true. User command must be all. Channel command must be the channel were join messages are sent by defualt.\n"
                             "     UniqueUsers: Looks for when users were added to the server, and only counts unique personel. Same restrictions as the users command apply."),

            "overview" :    ("This bot was created to see more data about a specifc server. It is not 100% loss proof (funky stuff happens when deleting messages).\n"
                             "To see the source code, see https://github.com/Andallfor/infoBot.")
        }

        message = answers["default"]
        if len(keyWords) == 2 and keyWords[1].lower() in answers:
            message = answers[keyWords[1].lower()]
        
        await m.channel.send(message)
    
    async def ratio(self, m, keyWords):
        ######################################################
        # GET USER VALUES                                    #
        ######################################################

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

        ######################################################
        # GET DATA                                           #
        ######################################################

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
        
        ######################################################
        # GENERATE PLOT                                      #
        ######################################################

        messageToSend = f'Found "{phrase}" a total of {total} times.\n'

        sortedUsers = sorted(users, key = users.get, reverse = True)

        names = sortedUsers[:min(len(sortedUsers), 10)]
        values = [users[user] for user in names]
        names = ["Unknown" if self.get_user(user) == None else self.get_user(user).display_name for user in names]

        file = util.quickPie(values, names, (9, 9), self.guildInfo[m.guild.id].guild, total)
        await m.channel.send(messageToSend, file = file)
    
    async def dRatio(self, m, keyWords):
        ######################################################
        # GET USER VALUES                                    #
        ######################################################
        if len(keyWords) < 3:
            await m.channel.send("Incorrect number of arguments recieved")
            return
        
        if keyWords[2] not in ["pins", "phrase"]:
            await m.channel.send(f'Did not recoginize dSort "{keyWords[2]}"')
            return
        sort = keyWords[2]

        if sort == "pins":
            if keyWords[1] != "all":
                await m.channel.send(f'Detected sort {keyWords[2]}. Setting users to "all".')
        
        if sort == "phrase":
            if keyWords[1] == "all":
                await m.channel.send(f'Detected sort {keyWords[2]}. This sort requires user to be a specific @.')
                return

        userToCheck = 0
        try:
            if keyWords[1] != "all":
                userToCheck = m.mentions[0].id
        except:
            m.channel.send(f'Did not recognize user "{keyWords[1]}"')
            return

        if sort == "phrase":
            if len(keyWords) < 4:
                await m.channel.send("Incorrect number of arguments recieved")
                return
            
            if keyWords[3] in ["default", "noncap", "discord", "noncapdiscord"]:
                frmat = keyWords[3]
            else:
                await m.channel.send(f'Unable to read given format "{keyWords[2]}"')
                return
            
            phrase = keyWords[4]
            if len(keyWords) >= 5:
                for continuedPhrase in m.content.split(' ')[5:]:
                    phrase += ' ' + continuedPhrase
        
        ######################################################
        # GET DATA                                           #
        ######################################################
        info = dict()
        total = 0
        for (c, value) in self.guildInfo[m.guild.id].channelInfo.items():
            for (day, messages) in value["content"].items():
                for message in messages:
                    if sort == "pins":
                        if message["type"][1] == 6:
                            if message["author"] not in info.keys():
                                info[message["author"]] = 0
                            info[message["author"]] += 1
                            total += 1
                    elif sort == "phrase":
                        if message["author"] == userToCheck:
                            if util.getFormat(frmat, phrase, message["content"]):
                                if message["author"] not in info.keys():
                                    info[message["author"]] = 0
                                info[message["author"]] += 1
                            else:
                                total += 1

        if sort == "pins":
            sortedUsers = sorted(info, key = info.get, reverse = True)

            names = sortedUsers[:min(len(sortedUsers), 10)]
            values = [info[user] for user in names]
            names = ["Unknown" if self.get_user(user) == None else self.get_user(user).display_name for user in names]

            file = util.quickPie(values, names, (9, 9), m.guild, total)
            await m.channel.send(f"A total of {total} pins have been made.", file = file)
            return
        elif sort == "phrase":
            await m.channel.send(f'{self.get_user(userToCheck)} has said "{phrase}" {info[userToCheck]} times, accounting for {round(info[userToCheck]/total, 2) * 100}% of their total messages.')
            return
                    
    
    async def common(self, m, keyWords):
        pass


    ######################################################
    # USER COMMANDS UTIL                                 #
    ######################################################
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


    ######################################################
    # REGULAR UTIL                                       #
    ######################################################
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