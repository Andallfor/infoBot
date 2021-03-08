import discord
import os
import sys
import timeit
import pickle
import guildClass

started = False

'''
todo:

save guilds with custom files
- use guild id as name
'''
class _client(discord.Client):
    async def on_ready(self):
        global started
        if started:
            return

        started = True        

        for g in self.guilds:
            gd = guildClass.guild()
            await gd.manualInit(g)
            
    
    async def on_message(self, message):
        # command to run bot is \
        if len(message.content) == 0 or message.content[0] != "\\" or message.author == self.user or not started:
            return
        
        await message.channel.send("Recieved command")
        '''
        Avaliable commands:
        \help
        \history user channel startTime endTime sort
            user, channel can be all
            startTime, endTime can be default
            sort can be totalMessages, and userChange
        \ratio phrase channel
        '''

        keyWords = message.content.split(' ')
        keyWords = [i.lower() for i in keyWords]

        for i in range(len(self.cached_messages)):
            await message.channel.send(self.cached_messages[i].content)

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
        else:
            await message.channel.send(f"Did not recognize command '{keyWords[0]}'\nUse \\help to see a list of all possible commands")
    
    async def ratio(self, phrase, channel):
        initT = timeit.default_timer()
        lst = channel.history(limit = 5000).get(author_name = "Andallfor")
        endT = timeit.default_timer()

        #await channel.send(f"Indexed {len(lst)} messages in {endT - initT}")
        await channel.send(lst)

client = _client()

if (len(sys.argv) != 2):
    sys.exit("Incorrect Usage. Input token along with command.")

token = sys.argv[1]
client.run(token)