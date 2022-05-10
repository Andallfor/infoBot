# TODO LIST:
- fix bugs and stuff (eta: sometime in the next few years)
# Info Bot
A general Dmscord bot that allows users to see various pieces of information about a server and the users within.  
See the [Usage](#usage) section for detailed information.

# Usage
Provided commands: [\help](#help), [\history](#history), [\ratio](#ratio), [\dRatio](#dratio), [\common](#common)  
Parameter information: [format](#format), [sort](#sort), [dsort](#dsort)
### Notes
1. If parameters are enclosed in a (), they are required together.
2. Optional parameters are position-sensitive. That is, if you provide a parameter at the end of a command, you must also provide each of the parameters before, even if they are not required.

### <a name="help"></a>\help
Gives information on how to use a certain function.
- Usage: \help command
  - Command: history, ratio, dRatio, dSort, common, overview, sort, format.
- Example: \help history

### <a name="history"></a>\history
Generates of a graph of the specified data.
- Usage: \history user channel startTime endTime sort ([format](#format) phrase)
  - User: Can be a specific @ or all. *Non-optional*
  - Channel: Can be a specific # or all. *Non-optional*
  - StartTime: A time in the format dd-mm-yyyy. *Optional*, defaults to creation of channel.
  - EndTime: A time in the format dd-mm-yyyy. *Optional*, defaults to current time, or use 0.
  - [Sort](#sort): Tells the bot what data to draw from. Use \\help sort to see possible commands. *Optional*, defaults to messages.
  - [Format](#format): Use [\help](#help) format to see possible commands. *Only used if the sort is "phrase"*.
  - Phrase: No particular format, but cannot contain a backslash. *Only used if the sort is "phrase"*.

### <a name="ratio"></a>\ratio
Finds the amount of times a phrase was said, and the users that said it. Resulting data may not add up to 100% (Don't question it).  
See also: [\dratio](#dratio)
- Usage: \ratio channel format phrase
  - Channel: Can be a specific # or all. *Non-optional*
  - Tells the program how to determine if a phrase is within a message. Use [\help](#help) format to see possible commands. *Non-optional*
  - Phrase: No particular format, but cannot contain a backslash. *Non-optional*  

### <a name="dratio"></a>\dratio
A more specific form of [\ratio](#ratio). Finds the ratio of specific elements instead of a phrase.
See also: [\ratio](#ratio)
- Usage: \dRatio user [dSort](#dsort) (format phrase)
  - User can be a specific @ or all. *Non-optional*
  - [dSort](#dsort): Tells the bot what data to look for. *Non-optional*

### <a name="common"></a>\common
Looks for the 20 most common words a user/server has said.
- Usage: \common user ignore customIgnore
  - User: Must be a specific @.
  - Ignore: Can be either ignoreCommon or ignoreCustom. *Non-optional*
    - ignoreCommon: Ignores the most common words. Still allows for additional custom ignores.
    - ignoreCustom: Only ignores words that the user inputs.
  - CustomIgnore: An input for words that will be ignored by the bot. *Optional*

### <a name="format"></a>Format Information
Specifies how to determine if a phrase is within another. Can be default, nonCap, discord, or nonCapDiscord.
- Default: Naively searches for a phrase. Is case-sensitive, and will include the result if it is found within another word.
- NonCap: Similar to default, however it is case-insensitive.
- Discord: Attempts to match the search to result discord provides in their search bar. Is case-sensetive.
- NonCapDiscord: Similar to discord, however it is case-insensitive.

### <a name="dsort"></a>dSort Information
Specifies what data that [\dRatio](#dratio) looks for.
- Pins: Looks for the total amount of pins. Requires user to be all.
- Phrase: Looks for the relationship between the times a user has said a certain phrase versus their total messages. Requies use of an additional [format](#format) and phrase command, and user must be a @.

### <a name="sort"></a>Sort Information
Specifies what data to draw from. Can be messages, phrase, pins, users and uniqueUsers.
- Phrase: Looks for a certain message. Requires the use of an additional [format](#format) and phrase command.
- Pins: Looks for when pins were added. Does not require any other arguments.
- Users: Looks for when users were added to the server. Server must have messages sent upon arrival to true. User command must be all. Channel command must be the channel were join messages are sent by default.
- UniqueUsers: Looks for when users were added to the server, and only counts unique personel. Same restrictions as the users command apply.

# Installation
The bot is self hosted, if you want to add it to your server you need to run it yourself- I am not making a universal version for 2 reasons:
1. I don't feel like it.
2. It would give me access to every message on each server the bot is connected to, which is not a good idea.

Steps:
1. Clone this repo
2. Create your own discord bot on the discord developer page.
3. Copy the bot's token.
4. Open the folder that contains the files (note that you your relative path must be the folder, as the program uses relative pathes).
5. Run `main.py` with the token as the only argument.
6. Wait until the bot prints "ready" into the terminal. Note that this may take a while as the bot needs to index the server that it is running on first.
