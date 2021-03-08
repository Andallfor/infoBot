import discord
import datetime
# possible opt: switch lists to sets?

class guild():
    async def manualInit(self, guild):
        self.guild = guild

        self.channels = [c for c in self.guild.text_channels]

        # channel : [lastMessageTime (as datetimeScore), [{datetimeScore : messages}]]
        # name : lastMessageTime, [formattedMsgs]
        self.channelInfo = dict()

        for c in self.channels:
            await self.initNewChannelInfo(c)
    
    async def checkForUpdates(self):
        self.channels = [c for c in self.guild.text_channels]

        for c in self.channels:
            if c in self.channelInfo:
                # oldValue < currentValue
                # the newest message saved is older then the current newest message
                if self.channelInfo[c][0] < self.datetimeScore((await c.fetch_message(c.last_message_id)).created_at):

                    # remove the lastMessageTime key and values from formattedMsgs
                    self.channelInfo[c][1].pop(self.channelInfo[c][0], None)
                    # get all msgs after lastMessageTime
                    formattedMessages = self.formatHistoryByDate(c.history(limit = None, after = self.channelInfo[c][0]))
                    # combine the two dicts
                    self.channelInfo[c][1].update(formattedMessages)

                    # set lastMessageTime to the new lastMessageTime
                    self.forceSetLatestMsg(c)
            else:
                self.initNewChannelInfo(c)

    async def initNewChannelInfo(self, c):
        self.channelInfo[c] = [
            0 if await c.fetch_message(c.last_message_id) == None else self.datetimeScore((await c.fetch_message(c.last_message_id)).created_at), 
            [await self.formatHistoryByDate(c.history(limit = None))]
        ] 
    
    async def forceSetLatestMsg(self, c, m = None):
        if m is not None:
            self.channelInfo[c][0] = self.datetimeScore((await c.fetch_message(c.last_message_id)).created_at)
        else:
            self.channelInfo[c][0] = self.datetimeScore(m.created_at)
    
    async def formatHistoryByDate(self, h):
        # returns a dictionary
        # datetime obj : [messages]
        rd = dict()

        async for msg in h:
            if msg.created_at not in rd:
                rd[self.datetimeScore(msg.created_at)] = [msg]
            else:
                rd[self.datetimeScore(msg.created_at)].append(msg)
        
        return rd
    
    # used to check if one datetime is greater then the other
    # ie if its more recent, it will be greater
    def datetimeScore(self, dt):
        return (dt.year * 10_000) + (dt.month * 100) + dt.day
    
    def year(self, score):
        return int(score / 10_000)
    
    def month(self, score):
        return int((score - (self.year(score) * 10_000)) / 100)
    
    def day(self, score):
        return int(score - ((self.year(score) * 10_000 ) + (self.month(score) * 100)))
                