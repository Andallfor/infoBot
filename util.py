import discord
import datetime
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdt

lLetters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
cLetters = [l.upper() for l in lLetters]
letters = lLetters + cLetters

def dtScore(dt):
    return int((dt.year * 10_000) + (dt.month * 100) + dt.day)
    
def cleanUTC(score):
    return datetime.datetime(year = year(score), month = month(score), day = day(score))

def year(score):
    return int(score / 10_000)

def month(score):
    return int((score - (year(score) * 10_000)) / 100)

def day(score):
    return int(score - ((year(score) * 10_000 ) + (month(score) * 100)))

def formatMsg(m):
    return {
            "created" : dtScore(m.created_at),
            "content" : m.content,
            "author" : m.author.id,
            "references" : [u.id for u in m.mentions],
            "id" : m.id,
            "type" : m.type
        }
def inputToDTScore(phrase):
    parts = phrase.split('-')
    return datetime.datetime(day = int(parts[0]), month = int(parts[1]), year = int(parts[2]))

def strDT(dt):
    return f"{dt.day}/{dt.month}/{str(dt.year)[2:]}"

def isValidDTScore(dtScore):
    # sue me
    try:
        cleanUTC(dtScore)
        return True
    except:
        return False

def getFormat(frmat, phrase, match):
    # auto lower case all messages if needed
    msg = str(match)
    if frmat in ["noncap", "noncapdiscord"]:
        phrase = phrase.lower()
        msg = match.lower()

        if frmat == "noncap":
            frmat = "default"
        else:
            frmat = "discord"

    contains = False
    if frmat == "default":
        if phrase in msg:
            contains = True
    elif frmat == "discord":
        index = msg.find(phrase)
        if index != -1:
            contains = True

            # is the start of the string, so nothing is before it
            if index != 0:
                if msg[index - 1] in letters:
                    contains = False
            
            # if end of phrase is not at end of message
            if index + len(phrase) != len(msg):
                if msg[index + 1] in letters:
                    contains = False
    
    return contains

def quickPlot(data, labels, size, g, file, graph, isDate = False):
    # returns file
    fig, ax = plt.subplots(figsize = size)

    if graph == "bar":
        ax.bar(data[0], data[1], width = 1)
    elif graph == "line":
        ax.plot(data[0], data[1])
        
    ax.set(xlabel = labels[0], ylabel = labels[1])

    if isDate:
        dateForm = mdt.DateFormatter("%d-%m-%y")
        ax.xaxis.set_major_formatter(dateForm)

    plt.savefig(str(g.id) + '-history.png', bbox_inches = 'tight')
    plt.close()

    file = discord.File(str(g.id) + '-history.png', filename = 'data.png')

    os.remove(str(g.id) + '-history.png')

    return file