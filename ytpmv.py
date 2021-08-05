import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord
import asyncio
import re


class ytpmv:

    def __init__(self):
        self.msgQueue = []
        self.isBusy = False
        self.vidsToMerge = []
        self.codec = 'libvpx'


    async def sendHelp(self, message):

        embed = discord.Embed(
            colour=discord.Colour.teal(),
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
"""
            )

        await message.channel.send(embed=embed)



    async def addToQueue(self, message):

        #REPLACE LINE BREAKS WITH SPACES
        message.content = message.content.replace('\n', ' ')

        self.msgQueue.append(message)



    async def checkQueue(self):
        if self.msgQueue == [] or self.isBusy == True:
            return

        self.isBusy == True
        message = self.msgQueue[0]

        #CLEAR TEMP
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


        elif message.content.lower().startswith('ytpmvbot '):
            await self.run(message)


        self.msgQueue.pop(0)
        self.isBusy == False



    def clearTemp(self):
        if os.path.exists('temp'):
            shutil.rmtree('temp')
        os.mkdir('temp')


    async def run(self, message):

        #CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            return

        #ADD REACTION
        await message.add_reaction(emoji='⌚')


        #PARSE MESSAGE
        try:
            notes, bpm = self.parseMessage(message.content)
        except:
            await message.reply('Parsing error')
            return


        #SAVE ORIGINAL SAMPLE
        try:
            filename = await self.saveAttachmentOrRef(message)
        except:
            await message.reply('Sample file error')
            return

        #RENDER VIDEO CLIPS
        try:
            await self.renderFlippedVid(filename)
        except:
            await message.reply('Video rendering error')
            return

        #RENDER PITCHED SAMPLES
        try:
            await self.renderPitchedSamples(notes)
        except:
            await message.reply('Audio rendering error')
            return

        #RENDER YTPMV
        try:
            await self.renderYTPMV(notes, bpm)
        except:
            await message.reply('Video rendering error')
            return

        #SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/ytpmvbot.webm'))
        except:
            await message.reply('File too big')



    def parseMessage(self, content):

        content = self.addSpacesInbetweenBrackets(content)
        content = self.deleteDoubleSpaces(content)
        notes, bpm, pitchOffset = self.parseArgs(content)
        notes = self.parseNotes(notes, pitchOffset)

        return notes, bpm



    def parseNotes(self, notes, pitchOffset):
        notes = ' '.join(notes)

        depth = 0
        notes = notes.split(' ')
        maxdepth = 0
        deptharray = []
        for i in notes:
            if i=='[':
                depth+=1
            deptharray.append([i,depth])
            if ']' in i:
                depth-=1
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
                    loop = deptharray[startindex+1:endindex]
                    for i in range(repeatCount-1):
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
            if content[i] == '[' and content[i+1] != ' ':
                newcontent.append(content[i])
                newcontent.append(' ')
            elif content[i] == ']' and content[i-1] != ' ':
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
        notes = newnotes[1:]
        return notes


    def parseArgs(self, notes):
        bpm = 120
        if '-bpm' in notes:
            index = notes.index('-bpm') + 1
            bpm = float(notes[index])
            notes.pop(index-1)
            notes.pop(index-1)

        if not 30 < bpm < 600:
            raise Exception

        pitchOffset = 0
        if '-pitchoffset' in notes:
            index = notes.index('-pitchoffset') + 1
            pitchOffset = float(notes[index])
            notes.pop(index-1)
            notes.pop(index-1)

        if not -25 < pitchOffset < 25:
            raise Exception

        return notes, bpm, pitchOffset


    async def renderFlippedVid(self,filename):

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
            rateFromPitch = 2**(i/12)
            if not 0.01 < rateFromPitch < 100:
                raise Exception

            pitchedSample = ffmpeg.input('temp/samp1.webm').audio.filter('rubberband', pitch=rateFromPitch)
            out = ffmpeg.output(pitchedSample, f'temp/samp{i}.ogg')
            out.run()



    async def renderYTPMV(self, notes, bpm):

        timelineV = []
        timelineA = []
        flipSwitch = 1
        timer = 0.0


        #MAKE FILE DICTS
        audioDict = {}
        for i in notes:
            pitch = i[0]
            if pitch in audioDict.keys():
                continue
            elif pitch != '':
                audioDict.update({pitch: AudioFileClip(f'temp/samp{pitch}.ogg')})
            else:
                continue

        videoDict = {'samp1': VideoFileClip(f"temp/samp1.webm"), 'samp-1': VideoFileClip(f"temp/samp-1.webm")}

        for i in notes:
            pitch = i[0]
            length = i[1]*60/bpm
       
            if pitch != '':
                audio = audioDict[pitch].copy()
                clip = videoDict[f'samp{flipSwitch}'].copy()

                clip.start = timer
                audio.start = timer

                if length < clip.duration and length < audio.duration:
                    clip.end = timer+length
                    audio.end = timer+length
                else:
                    clip.end = timer+clip.duration
                    audio.end = timer+audio.duration

                flipSwitch *= -1

                timelineV.append(clip)
                timelineA.append(audio)

            timer += length

        final_Vclip = CompositeVideoClip(timelineV)
        final_Aclip = CompositeAudioClip(timelineA)
        final_Vclip.audio = final_Aclip
        final_Vclip.resize(width=420).write_videofile(f"./temp/ytpmvbot.webm", codec=self.codec)


        #CLOSE CLIPS
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

        #CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            raise Exception

        #SAVE ORIGINAL SAMPLE
        if message.attachments != []:
            attachment = message.attachments[0]
        else:
            referencedMessage = await message.channel.fetch_message(message.reference.message_id)
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

        #SAVE ORIGINAL SAMPLE
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
            clip.resize(width=420).write_videofile('./temp/trimmed.webm', codec=self.codec)
        except:
            await message.reply('Video rendering error')
        else:
            #SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/trimmed.webm'))
            except:
                await message.reply('File too big')
        finally:
            #CLOSE CLIPS
            clip.close()



    async def volume(self, message):

        msgSplit = message.content.split(' ')
        try:
            volRate = float(msgSplit[2])
        except:
            await message.reply('Volume multiplier value error')
            return

        await message.add_reaction(emoji='⌚')

        #SAVE ORIGINAL SAMPLE
        try:
            filename = await self.saveAttachmentOrRef(message)
        except:
            await message.reply('Sample file error')
            return


        clip = VideoFileClip(f'./temp/{filename}')

        try:
            clip = clip.volumex(volRate)
            clip.resize(width=420).write_videofile('./temp/volume.webm', codec=self.codec)
        except:
            await message.reply('Video rendering error')
        else:
            #SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/volume.webm'))
            except:
                await message.reply('File too big')
        finally:
            #CLOSE CLIPS
            clip.close()


    async def add(self, message):

        if len(self.vidsToMerge) == 4:
            await message.reply('Can add max 4 videos. Send \'ytpmvbot reset\' to start over.')
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
            #SAVE ORIGINAL SAMPLE
            try:
                filename = await self.saveAttachmentOrRef(i, prefix=f'merge_{counter}')
            except:
                await message.reply('Video file error. Send \'ytpmvbot reset\' to start over.')
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
                final_clip = clips_array([ [ tracks[0] ], [ tracks[1] ] ])
            else:
                final_clip = clips_array([tracks])

        elif len(filenames) == 3:
            final_clip = clips_array([tracks[:2]])
            final_clip = clips_array([ [ final_clip ], [ tracks[2] ] ])

        elif len(filenames) == 4:
            top = tracks[:2]
            bottom = tracks[2:]
            final_clip = clips_array([top, bottom])

        try:
            final_clip.resize(width=420).write_videofile(f'./temp/ytpmvmbot.webm', codec=self.codec)
        except:
            await message.reply('Video rendering error')
        else:
            #SEND FILE TO DISCORD
            try:
                await message.reply(file=discord.File(f'./temp/ytpmvmbot.webm'))
            except:
                await message.reply('File too big')
        finally:
            #CLOSE CLIPS
            for i in tracks:
                i.close()

            final_clip.close()
            await self.reset(message)


#DISCORD BOT HERE

KEY = open('./key').read()
client = discord.Client()
ytpmv = ytpmv()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    #BACKGROUND QUEUE CHECK
    while not client.is_closed():
        await ytpmv.checkQueue()
        await asyncio.sleep(1)

@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if message.content.lower().startswith('ytpmvbot'):
        await ytpmv.addToQueue(message)



client.run(KEY)
