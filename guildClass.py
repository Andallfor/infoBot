import datetime
import json
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
                            id : 0
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
                if self.channelInfo[c]["lastMessageTime"] <= self.dtScore((await c.fetch_message(c.last_message_id)).created_at):
                    # remove the lastMessageTime key and values from formattedMsgs
                    self.channelInfo[c]["content"][int(self.channelInfo[c]["lastMessageTime"])] = []
                    # get all msgs after lastMessageTime
                    # cleanUTC just gives the day that it was posted, with the time values being set to 0
                    formattedMessages = await self.formatHistoryByDate(c.history(limit = None, after = self.cleanUTC(self.channelInfo[c]["lastMessageTime"])))

                    # combine the two dicts
                    self.channelInfo[c]["content"].update(formattedMessages)

                    # set lastMessageTime to the new lastMessageTime
                    await self.forceSetLatestMsg(c)
            else:
                await self.initNewChannelInfo(c)

    async def initNewChannelInfo(self, c):
        # no msgs have been sent in channel
        try:
            await c.fetch_message(c.last_message_id)
        except:
            return

        # init base structure
        self.channelInfo[c] = {
            "lastMessageTime" : self.dtScore((await c.fetch_message(c.last_message_id)).created_at),
            "content" : {}
        }

        # fill in values
        allMessages = await c.history(limit = None).flatten()

        for m in allMessages:
            if int(self.dtScore(m.created_at)) not in self.channelInfo[c]["content"]:
                self.channelInfo[c]["content"][int(self.dtScore(m.created_at))] = []

            self.channelInfo[c]["content"][int(self.dtScore(m.created_at))].append(self.formatMsg(m))

    async def newMsg(self, c, m):
        await self.forceSetLatestMsg(c, m)
        # can use lastMessageTime bc self.forceSetLastestMsg sets lastMessageTime to
        # m's created_at time
        self.channelInfo[c]["content"][self.channelInfo[c]["lastMessageTime"]].append(self.formatMsg(m))

    async def forceSetLatestMsg(self, c, m = None):
        if m is None:
            self.channelInfo[c]["lastMessageTime"] = self.dtScore((await c.fetch_message(c.last_message_id)).created_at)
        else:
            self.channelInfo[c]["lastMessageTime"] = self.dtScore(m.created_at)
        
        # if a new day is created
        if self.channelInfo[c]["lastMessageTime"] not in self.channelInfo[c]["content"]:
            self.channelInfo[c]["content"].update({self.channelInfo[c]["lastMessageTime"] : []})
    
    async def formatHistoryByDate(self, h):
        # returns a dictionary
        # {datetime obj : [messages]}
        rd = dict()

        async for msg in h:
            if self.dtScore(msg.created_at) not in rd:
                rd[self.dtScore(msg.created_at)] = [self.formatMsg(msg)]
            else:
                rd[self.dtScore(msg.created_at)].append(self.formatMsg(msg))
        
        return rd
    
    def formatMsg(self, m):
        return {
                "created" : self.dtScore(m.created_at),
                "content" : m.content,
                "author" : m.author.id,
                "references" : [u.id for u in m.mentions],
                "id" : m.id
            }
    
    # used to check if one datetime is greater then the other
    # ie if its more recent, it will be greater
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
                