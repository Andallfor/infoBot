import discord
import datetime

class guild():
    async def manualInit(self, guild):
        self.guild = guild

        self.channels = [c for c in self.guild.text_channels]


        # channel : [lastMessageTime, [allChannelMessages]]
        self.channelInfo = dict()

        for c in self.channels:
            await self.initNewChannelInfo(c)
    
    async def checkForUpdates(self):
        self.channels = [c for c in self.guild.text_channels]

        for c in self.channels:
            if c in self.channelInfo:
                if self.datetimeScore(self.channelInfo[c]) < (await c.fetch_message(c.last_message_id)).created_at:
                    # the newest message saved is older then the current newest message
                    # oldValue < currentValue
                    self.forceSetLatestMsg(c)

                    # update messages
            else:
                self.initNewChannelInfo(c)

    async def initNewChannelInfo(self, c):
        self.channelInfo[c] = [0 if await c.fetch_message(c.last_message_id) == None else (await c.fetch_message(c.last_message_id)).created_at, [await c.history(limit = None).flatten()]] 
    
    async def forceSetLatestMsg(self, c, m = None):
        if m is not None:
            self.channelInfo[c][0] = (await c.fetch_message(c.last_message_id)).created_at
        else:
            self.channelInfo[c][0] = m.created_at
    
    # used to check if one datetime is greater then the other
    # ie if its more recent, it will be greater
    def datetimeScore(self, dt):
        return (dt.year * 365) + (dt.month * 12) + dt.day
                