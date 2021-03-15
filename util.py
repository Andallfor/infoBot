import discord
import datetime


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