import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord
from discord.ext import tasks
import asyncio
import re
import json


class ytpmv:
    def __init__(self):
        self.msgQueue = []
        self.isBusy = False
        self.vidsToMerge = []
        self.codec = 'libvpx'

    async def sendHelp(self, message):

        embed = discord.Embed(
            colour=discord.Colour.blue(),
            title='ytpmvbot help - click for more',
            url='https://github.com/efpi-bot/ytpmvbot',
        )
        embed.add_field(
            name='Available commands:',
            value="""• ytpmvbot pitch/duration [...]
• ytpmvbot trim
• ytpmvbot volume
• ytpmvbot add
• ytpmvbot reset
• ytpmvbot merge
• ytpmvbot concat
• ytpmvbot register
• ytpmvbot search
• ytpmvbot show
• ytpmvbot make
• ytpmvbot delete
""",
        )

        await message.channel.send(embed=embed)

    async def addToQueue(self, message):

        # REPLACE LINE BREAKS WITH SPACES
        message.content = message.content.replace('\n', ' ')

        self.msgQueue.append(message)

    async def checkQueue(self):
        if self.msgQueue == [] or self.isBusy == True:
            return

        self.isBusy == True
        message = self.msgQueue[0]

        # CLEAR TEMP
        self.clearTemp()

        if message.content.lower() == 'ytpmvbot add':
            await self.add(message)

        elif message.content.lower() == 'ytpmvbot merge':
            await self.merge(message)

        elif message.content.lower() == 'ytpmvbot vmerge':
            await self.merge(message, vertical=True)

        elif message.content.lower() == 'ytpmvbot concat':
            await self.merge(message, concat=True)

        elif message.content.lower() == 'ytpmvbot reset':
            await self.reset(message)

        elif message.content.lower() == 'ytpmvbot help':
            await self.sendHelp(message)

        elif message.content.lower().startswith('ytpmvbot trim'):
            await self.trim(message)

        elif message.content.lower().startswith('ytpmvbot volume'):
            await self.volume(message)

        elif message.content.lower().startswith('ytpmvbot register'):
            await self.registerPattern(message)

        elif message.content.lower().startswith('ytpmvbot delete'):
            await self.delPattern(message)

        elif message.content.lower().startswith('ytpmvbot show'):
            await self.showPattern(message)

        elif message.content.lower().startswith('ytpmvbot search'):
            await self.searchPattern(message)

        elif message.content.lower().startswith('ytpmvbot make'):
            await self.run(message, make=True)

        elif message.content.lower().startswith('ytpmvbot '):
            await self.run(message)

        self.msgQueue.pop(0)
        self.isBusy == False

    def clearTemp(self):
        if os.path.exists('temp'):
            shutil.rmtree('temp')
        os.mkdir('temp')

    async def run(self, message, make=False):

        # CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            return

        # ADD REACTION
        await message.add_reaction(emoji='⌚')

        # PARSE MESSAGE
        try:
            if make == True:
                notes, bpm = self.parseMakeMessage(message.content)
            else:
                notes, bpm = self.parseMessage(message.content)
        except:
            await message.reply('Parsing error')
            return

        # SAVE ORIGINAL SAMPLE
        try:
            filename = await self.saveAttachmentOrRef(message)
        except:
            await message.reply('Sample file error')
            return

        # RENDER VIDEO CLIPS
        try:
            await self.renderFlippedVid(filename)
        except:
            await message.reply('Video rendering error')
            return

        # RENDER PITCHED SAMPLES
        try:
            await self.renderPitchedSamples(notes)
        except:
            await message.reply('Audio rendering error')
            return

        # RENDER YTPMV
        try:
            await self.renderYTPMV(notes, bpm)
        except:
            await message.reply('Video rendering error')
            return

        # SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/ytpmvbot.webm'))
        except:
            await message.reply('File too big')

    def parseMessage(self, content):

        content = self.addSpacesInbetweenBrackets(content)
        content = self.deleteDoubleSpaces(content)

        # DELETING PREFIX
        content = content[1:]

        notes, bpm, pitchOffset = self.parseArgs(content)
        notes = self.parseNotes(notes, pitchOffset)

        return notes, bpm

    def parseMakeMessage(self, content):
        content = self.deleteDoubleSpaces(content)

        # DELETING PREFIX
        content = content[2:]
        content, bpmOverride, pitchOffsetOverride = self.parseArgs(content)

        content = ' '.join(content)

        pattern = self.getPattern(content)
        pattern = self.addSpacesInbetweenBrackets(pattern)
        pattern = self.deleteDoubleSpaces(pattern)
        notes, bpm, pitchOffset = self.parseArgs(pattern)

        # ARGS OVERRIDE
        if pitchOffsetOverride != None:
            pitchOffset = pitchOffsetOverride
        if bpmOverride != None:
            bpm = bpmOverride

        notes = self.parseNotes(notes, pitchOffset)

        return notes, bpm

    def parseNotes(self, notes, pitchOffset):
        notes = ' '.join(notes)

        if pitchOffset == None:
            pitchOffset = 0

        depth = 0
        notes = notes.split(' ')
        maxdepth = 0
        deptharray = []
        for i in notes:
            if i == '[':
                depth += 1
            deptharray.append([i, depth])
            if ']' in i:
                depth -= 1
            if depth > maxdepth:
                maxdepth = depth

        parsedArray = []
        while maxdepth > 0:
            parsedArray.clear()
            for i in range(len(deptharray)):
                if deptharray[i] == ['[', maxdepth]:
                    startindex = i
                elif deptharray[i][0][0] == ']' and deptharray[i][1] == maxdepth:
                    repeatCount = int(deptharray[i][0].split(']')[1])
                    endindex = i
                    loop = deptharray[startindex + 1 : endindex]
                    for i in range(repeatCount - 1):
                        for k in loop:
                            parsedArray.append(k)
                else:
                    parsedArray.append(deptharray[i])

            deptharray = parsedArray.copy()

            maxdepth -= 1

        finalArray = []
        for i in deptharray:
            pitch = i[0].split('/')[0]

            if pitch != '':
                pitch = float(pitch) + pitchOffset

            duration = float(i[0].split('/')[1])
            finalArray.append([pitch, duration])
        return finalArray

    def addSpacesInbetweenBrackets(self, content):
        newcontent = []
        for i in range(len(content)):
            if content[i] == '[' and content[i + 1] != ' ':
                newcontent.append(content[i])
                newcontent.append(' ')
            elif content[i] == ']' and content[i - 1] != ' ':
                newcontent.append(' ')
                newcontent.append(content[i])
            else:
                newcontent.append(content[i])

        newcontent = ''.join(newcontent)
        return newcontent

    def deleteDoubleSpaces(self, content):
        notes = content.split(' ')
        newnotes = []
        for i in notes:
            if i != '':
                newnotes.append(i)

        return newnotes

    def parseArgs(self, notes):
        bpm = None
        if '-bpm' in notes:
            index = notes.index('-bpm') + 1
            bpm = float(notes[index])
            notes.pop(index - 1)
            notes.pop(index - 1)

            if not 30 < bpm < 600:
                raise Exception

        pitchOffset = None
        if '-pitchoffset' in notes:
            index = notes.index('-pitchoffset') + 1
            pitchOffset = float(notes[index])
            notes.pop(index - 1)
            notes.pop(index - 1)

            if not -25 < pitchOffset < 25:
                raise Exception

        return notes, bpm, pitchOffset

    async def renderFlippedVid(self, filename):

        inVid = ffmpeg.input(f'./temp/{filename}')
        inFlipVid = inVid.video.hflip()

        outVid = ffmpeg.output(inVid, 'temp/samp1.webm')
        outVid.run()

        outFlip = ffmpeg.output(inFlipVid, 'temp/samp-1.webm')
        outFlip.run()

    async def renderPitchedSamples(self, notes):

        uniqueNotes = []
        for i in notes:

            if i[0] == '':
                continue

            elif i[0] not in uniqueNotes:
                uniqueNotes.append(i[0])

        for i in uniqueNotes:
            rateFromPitch = 2 ** (i / 12)
            if not 0.01 < rateFromPitch < 100:
                raise Exception

            pitchedSample = ffmpeg.input('temp/samp1.webm').audio.filter(
                'rubberband', pitch=rateFromPitch
            )
            out = ffmpeg.output(pitchedSample, f'temp/samp{i}.ogg')
            out.run()

    async def renderYTPMV(self, notes, bpm):

        if bpm == None:
            bpm = 120

        timelineV = []
        timelineA = []
        flipSwitch = 1
        timer = 0.0

        # MAKE FILE DICTS
        audioDict = {}
        for i in notes:
            pitch = i[0]
            if pitch in audioDict.keys():
                continue
            elif pitch != '':
                audioDict.update({pitch: AudioFileClip(f'temp/samp{pitch}.ogg')})
            else:
                continue

        videoDict = {
            'samp1': VideoFileClip(f"temp/samp1.webm"),
            'samp-1': VideoFileClip(f"temp/samp-1.webm"),
        }

        for i in notes:
            pitch = i[0]
            length = i[1] * 60 / bpm

            if pitch != '':
                audio = audioDict[pitch].copy()
                clip = videoDict[f'samp{flipSwitch}'].copy()

                clip.start = timer
                audio.start = timer

                if length < clip.duration and length < audio.duration:
                    clip = clip.subclip(0, length)
                    audio = audio.subclip(0, length)
                else:
                    clip.end = timer + clip.duration
                    audio.end = timer + audio.duration

                flipSwitch *= -1

                timelineV.append(clip)
                timelineA.append(audio.audio_fadeout(0.01))

            timer += length

        final_Vclip = CompositeVideoClip(timelineV)
        final_Aclip = CompositeAudioClip(timelineA)
        final_Vclip.audio = final_Aclip
        final_Vclip.resize(width=420).write_videofile(
            f"./temp/ytpmvbot.webm", codec=self.codec
        )

        # CLOSE CLIPS
        for i in audioDict.values():
            i.close()

        for i in videoDict.values():
            i.close()

        for i in timelineV:
            i.close()

        for i in timelineA:
            i.close()

        final_Vclip.close()
        final_Aclip.close()

    async def saveAttachmentOrRef(self, message, prefix='sample_'):

        # CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            raise Exception

        # SAVE ORIGINAL SAMPLE
        if message.attachments != []:
            attachment = message.attachments[0]
        else:
            referencedMessage = await message.channel.fetch_message(
                message.reference.message_id
            )
            try:
                attachment = referencedMessage.attachments[0]
            except:
                raise Exception

        if not attachment.content_type.startswith('video'):
            raise Exception

        filename = prefix + attachment.filename
        print(filename)

        file = open(f'./temp/{filename}', 'wb')
        await attachment.save(file)

        file.close()
        return filename

    async def trim(self, message):

        msgSplit = message.content.split(' ')
        try:
            start = float(msgSplit[2])
            end = float(msgSplit[3])
        except:
            await message.reply('Start/end value error')
            return

        await message.add_reaction(emoji='⌚')

        # SAVE ORIGINAL SAMPLE
        try:
            filename = await self.saveAttachmentOrRef(message)
        except:
            await message.reply('Sample file error')
            return

        clip = VideoFileClip(f'./temp/{filename}')

        if end > clip.duration:
            end = clip.duration

        try:
            clip = clip.subclip(start, end)
            clip.resize(width=420).write_videofile(
                './temp/trimmed.webm', codec=self.codec
            )
        except:
            await message.reply('Video rendering error')
        else:
            # SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/trimmed.webm'))
            except:
                await message.reply('File too big')
        finally:
            # CLOSE CLIPS
            clip.close()

    async def volume(self, message):

        msgSplit = message.content.split(' ')
        try:
            volRate = float(msgSplit[2])
        except:
            await message.reply('Volume multiplier value error')
            return

        await message.add_reaction(emoji='⌚')

        # SAVE ORIGINAL SAMPLE
        try:
            filename = await self.saveAttachmentOrRef(message)
        except:
            await message.reply('Sample file error')
            return

        clip = VideoFileClip(f'./temp/{filename}')

        try:
            clip = clip.volumex(volRate)
            clip.resize(width=420).write_videofile(
                './temp/volume.webm', codec=self.codec
            )
        except:
            await message.reply('Video rendering error')
        else:
            # SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/volume.webm'))
            except:
                await message.reply('File too big')
        finally:
            # CLOSE CLIPS
            clip.close()

    async def add(self, message):

        if len(self.vidsToMerge) == 4:
            await message.reply(
                'Can add max 4 videos. Send \'ytpmvbot reset\' to start over.'
            )
            return

        self.vidsToMerge.append(message)
        await message.add_reaction(emoji='🎬')

    async def reset(self, message):
        self.vidsToMerge = []
        await message.add_reaction(emoji="👌")

    async def merge(self, message, concat=False, vertical=False):

        if len(self.vidsToMerge) < 2:
            await message.reply('Add some videos first!')
            return

        await message.add_reaction(emoji='⌚')

        counter = 0
        filenames = []
        for i in self.vidsToMerge:
            # SAVE ORIGINAL SAMPLE
            try:
                filename = await self.saveAttachmentOrRef(i, prefix=f'merge_{counter}')
            except:
                await message.reply(
                    'Video file error. Send \'ytpmvbot reset\' to start over.'
                )
                return

            filenames.append(filename)
            counter += 1

        tracks = []
        counter = 0
        for i in filenames:
            clip = VideoFileClip(f"./temp/{i}")
            tracks.append(clip)
            counter += 1

        if concat == True:
            final_clip = concatenate_videoclips(tracks, method='compose')

        elif len(filenames) == 2:

            if vertical == True:
                final_clip = clips_array([[tracks[0]], [tracks[1]]])
            else:
                final_clip = clips_array([tracks])

        elif len(filenames) == 3:
            final_clip = clips_array([tracks[:2]])
            final_clip = clips_array([[final_clip], [tracks[2]]])

        elif len(filenames) == 4:
            top = tracks[:2]
            bottom = tracks[2:]
            final_clip = clips_array([top, bottom])

        try:
            final_clip.resize(width=420).write_videofile(
                f'./temp/ytpmvmbot.webm', codec=self.codec
            )
        except:
            await message.reply('Video rendering error')
        else:
            # SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/ytpmvmbot.webm'))
            except:
                await message.reply('File too big')
        finally:
            # CLOSE CLIPS
            for i in tracks:
                i.close()

            final_clip.close()
            await self.reset(message)

    def readJson(self):
        file = open('./registered.json', 'r')
        registeredDict = json.loads(file.read())
        file.close()
        return registeredDict

    def writeJson(self, registeredDict):
        file = open('./registered.json', 'w')
        jsonfile = json.dumps(registeredDict, sort_keys=True, indent=4)
        file.write(jsonfile)
        file.close()

    async def registerPattern(self, message):

        command = message.content.split(' ')[2:]
        command = ' '.join(command)
        command = command.split(',')

        if len(command) != 3:
            await message.reply(
                'Usage: ytpmvbot register <title>, <instrument>, <pattern>'
            )
            return

        title = command[0].strip()
        channel = command[1].strip()
        pattern = command[2].strip()

        # STRIP YTPMVBOT WORD
        if pattern.startswith('ytpmvbot '):
            pattern = pattern[9:]

        newObj = {"title": title, "fields": [{"name": channel, "value": pattern}]}

        registeredDict = await self.modifyRegisteredFile(newObj)
        self.writeJson(registeredDict)
        await message.add_reaction(emoji='💾')

    async def modifyRegisteredFile(self, newObj):
        title = newObj["title"]
        channel = newObj["fields"][0]["name"]

        try:
            registeredDict = self.readJson()
        except:
            await message.reply('Invalid json file.')
            return

        existingFieldIndex = None

        if registeredDict != []:
            for i in registeredDict:
                if title.lower() == i["title"].lower():
                    for field in i["fields"]:
                        if channel.lower() == field["name"].lower():
                            existingFieldIndex = i["fields"].index(field)

                    if existingFieldIndex != None:
                        i["fields"].pop(existingFieldIndex)

                    i["fields"].append(newObj["fields"][0])
                    i["title"] = title
                    return registeredDict

        registeredDict.append(newObj)
        return registeredDict

    async def showPattern(self, message):
        searchPhrase = message.content.lower().split(' ')[2:]
        searchPhrase = ' '.join(searchPhrase)

        registeredDict = self.readJson()

        for song in registeredDict:
            if searchPhrase.lower() == song["title"].lower():
                embed = discord.Embed.from_dict(song)
                embed.colour = discord.Colour.blue()
                try:
                    await message.reply(embed=embed)
                except:
                    file = open('./temp/song.json', 'w')
                    jsonfile = json.dumps(song, sort_keys=True, indent=4)
                    file.write(jsonfile)
                    file.close()
                    await message.reply(
                        'Too many characters. Sending json file.',
                        file=discord.File('./temp/song.json'),
                    )
                return
        await message.reply('No matching title. Try ytpmvbot search <phrase>')

    async def searchPattern(self, message):
        searchPhrase = message.content.lower().split(' ')[2:]
        searchPhrase = ' '.join(searchPhrase)

        registeredDict = self.readJson()
        searchResults = []
        for song in registeredDict:
            if searchPhrase.lower() in song["title"].lower():
                searchResults.append(song["title"])

        searchResults = sorted(searchResults, key=str.lower)

        if searchPhrase == '':
            searchPhrase = 'all'

        if searchResults != []:
            embed = discord.Embed(
                title=f'Search results for {searchPhrase}:',
                description='\n'.join(searchResults),
                colour=discord.Colour.blue(),
            )
            await message.reply(embed=embed)
        else:
            await message.reply('No results.')

    def getPattern(self, phrase):
        content = phrase.split(',')
        title = content[0].strip()
        channel = content[1].strip()

        registeredDict = self.readJson()
        for i in registeredDict:
            if title.lower() == i["title"].lower():
                for field in i["fields"]:
                    if channel.lower() == field["name"].lower():
                        return field["value"]

    async def delPattern(self, message):
        phrase = message.content.lower().split(' ')[2:]
        phrase = ' '.join(phrase)
        phrase = phrase.split(',')

        if len(phrase) != 2:
            await message.reply('Usage: ytpmvbot delete <title>, <instrument>')
            return

        title = phrase[0].strip()
        channel = phrase[1].strip()

        registeredDict = self.readJson()
        indexSong = None
        indexChannel = None
        for i in registeredDict:
            if title.lower() == i["title"].lower():
                indexSong = registeredDict.index(i)
                for field in i["fields"]:
                    if channel.lower() == field["name"].lower():
                        indexChannel = i["fields"].index(field)

        if indexSong != None and indexChannel != None:
            registeredDict[indexSong]["fields"].pop(indexChannel)
            self.writeJson(registeredDict)
            await message.add_reaction(emoji='💾')
        else:
            await message.reply('No matching pattern.')


# DISCORD BOT HERE

KEY = open('./key').read()
client = discord.Client()
ytpmv = ytpmv()


# BACKGROUND QUEUE CHECK
@tasks.loop(seconds=1)
async def bgcheck():
    await ytpmv.checkQueue()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower().startswith('ytpmvbot'):
        await ytpmv.addToQueue(message)


bgcheck.start()
client.run(KEY)
