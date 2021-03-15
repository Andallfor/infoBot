import datetime
import json
import discord
from discord.enums import MessageType
import util
# possible opt: switch lists to sets?

class guild():
    async def manualInit(self, guild):
        self.guild = guild

        self.channels = [c for c in self.guild.text_channels]

        '''
        {
            name : int
            {
                lastMessageTime : int
                content : str
                {
                    day : int
                    [
                        {
                            created : datetimeScore  # bit redudent, but just incase
                            content : str
                            owner : int
                            references : [int]
                            id : int
                            type : int
                        }
                    ]
                }
            }
        }
        '''
        self.channelInfo = dict()

        for c in self.channels:
            await self.initNewChannelInfo(c)

    def loadFromDir(self, guild, path):
        self.guild = guild
        self.channels = [c for c in self.guild.text_channels]
        self.channelInfo = dict()

        d = json.load(open(path, "r"))

        # switch out keys for the actual text channel
        # this is just bc im lazy and dont want to be consistent
        # sue me
        for (key, item) in d.items():
            c = guild.get_channel(int(key))
            if c is not None:
                modifiedContent = dict()
                for (_key, _item) in item["content"].items():
                    modifiedContent[int(_key)] = _item
                
                self.channelInfo[c] = {"lastMessageTime" : item["lastMessageTime"], "content" : modifiedContent}
    
    async def checkForUpdates(self):
        self.channels = [c for c in self.guild.text_channels]

        for c in self.channels:
            if c in self.channelInfo.keys():
                # oldValue < currentValue
                # the newest message saved is older then the current newest message
                lastMsg = (await c.history(limit = 1).flatten())
                if len(lastMsg) == 0:
                    continue
                else:
                    lastMsg = util.dtScore(lastMsg[0].created_at)

                if self.channelInfo[c]["lastMessageTime"] <= lastMsg:
                    # remove the lastMessageTime key and values from formattedMsgs
                    self.channelInfo[c]["content"][int(self.channelInfo[c]["lastMessageTime"])] = []
                    # get all msgs after lastMessageTime
                    # cleanUTC just gives the day that it was posted, with the time values being set to 0
                    formattedMessages = await self.formatHistoryByDate(c.history(limit = None, after = util.cleanUTC(self.channelInfo[c]["lastMessageTime"])))

                    # combine the two dicts
                    self.channelInfo[c]["content"].update(formattedMessages)

                    # set lastMessageTime to the new lastMessageTime
                    await self.forceSetLatestMsg(c)
            else:
                await self.initNewChannelInfo(c)

    async def initNewChannelInfo(self, c):
        # no msgs have been sent in channel

        lastMsg = (await c.history(limit = 1).flatten())
        if len(lastMsg) == 0:
            lastMsg = 0
        else:
            lastMsg = util.dtScore(lastMsg[0].created_at)

        # init base structure
        self.channelInfo[c] = {
            "lastMessageTime" : lastMsg,
            "content" : {}
        }

        # fill in values
        allMessages = await c.history(limit = None).flatten()

        for m in allMessages:
            if int(util.dtScore(m.created_at)) not in self.channelInfo[c]["content"]:
                self.channelInfo[c]["content"][int(util.dtScore(m.created_at))] = []

            self.channelInfo[c]["content"][int(util.dtScore(m.created_at))].append(util.formatMsg(m))

    async def newMsg(self, c, m):
        await self.forceSetLatestMsg(c, m)
        # can use lastMessageTime bc self.forceSetLastestMsg sets lastMessageTime to
        # m's created_at time
        self.channelInfo[c]["content"][self.channelInfo[c]["lastMessageTime"]].append(util.formatMsg(m))

    async def forceSetLatestMsg(self, c, m = None):
        if m is None:
            self.channelInfo[c]["lastMessageTime"] = util.dtScore((await c.history(limit = 1).flatten())[0].created_at)
        else:
            self.channelInfo[c]["lastMessageTime"] = util.dtScore(m.created_at)
        
        # if a new day is created
        if self.channelInfo[c]["lastMessageTime"] not in self.channelInfo[c]["content"]:
            self.channelInfo[c]["content"].update({self.channelInfo[c]["lastMessageTime"] : []})
    
    async def formatHistoryByDate(self, h):
        # returns a dictionary
        # {datetime obj : [messages]}
        rd = dict()

        async for msg in h:
            if util.dtScore(msg.created_at) not in rd:
                rd[util.dtScore(msg.created_at)] = [util.formatMsg(msg)]
            else:
                rd[util.dtScore(msg.created_at)].append(util.formatMsg(msg))
        
        return rd
                