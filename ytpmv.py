import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord
import asyncio


class ytpmv:

    def __init__(self):
        self.msgQueue = []
        self.isBusy = False
        self.vidsToMerge = []
        self.codec = 'libvpx'



    async def sendHelp(self, message):

        embed = discord.Embed(
            colour=discord.Colour.teal(),
            title='YTPMVbot help - click for more',
            url='https://github.com/efpi-bot/ytpmvbot',
            )
        embed.add_field(
            name='Available commands:',
            value="""• ytpmvbot help
• ytpmvbot pitch/duration [...]
• ytpmvbot trim
• ytpmvbot volume
• ytpmvbot add
• ytpmvbot merge
• ytpmvbot reset
"""
            )

        await message.channel.send(embed=embed)



    async def addToQueue(self, message):
        self.msgQueue.append(message)



    async def checkQueue(self):
        if self.msgQueue == [] or self.isBusy == True:
            return

        self.isBusy == True
        message = self.msgQueue[0]

        if message.content.lower() == 'ytpmvbot add':
            await self.add(message)

        elif message.content.lower() == 'ytpmvbot merge':
            await self.merge(message)

        elif message.content.lower() == 'ytpmvbot reset':
            await self.reset(message)

        elif message.content.lower() == 'ytpmvbot help':
            await self.sendHelp(message)

        elif message.content.lower().startswith('ytpmvbot trim '):
            await self.trim(message)

        elif message.content.lower().startswith('ytpmvbot volume '):
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

        content = message.content

        #CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            return

        #RESET TEMP FOLDER
        self.clearTemp()

        #ADD REACTION
        await message.add_reaction(emoji='⌚')

        #CREATE ARRAY OF NOTES
        notes = content[9:].split(' ')

        #SET BPM
        bpm = 120
        if '-bpm' in notes:
            bpm = float(notes[notes.index('-bpm') + 1])
            notes.pop(notes.index('-bpm')+1)
            notes.pop(notes.index('-bpm'))


        #SAVE ORIGINAL SAMPLE
        filename = await self.saveAttachmentOrRef(message)
        if filename == None:
            return


        #RENDER VIDEO CLIPS
        await self.renderFlippedVid(filename)


        #RENDER PITCHED SAMPLES
        if await self.renderPitchedSamples(notes) == 'error':
            await message.reply('wrong pitch value, aborting...')
            return

        #RENDER YTPMV
        if await self.renderYTPMV(notes, bpm) == 'error':
            await message.reply('wrong syntax, aborting...')
            return

        #SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/ytpmvbot.webm'))
        except:
            await message.reply('File too big, aborting...')



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
            notePitch = i.split('/')[0]

            if notePitch == '':
                continue

            try:
                int(notePitch)
            except:
                return 'error'
            if notePitch != '' and int(notePitch) not in uniqueNotes:
                uniqueNotes.append(int(notePitch))

        for i in uniqueNotes:

            rateFromPitch = 2**(i/12)
            if 100 < rateFromPitch < 0.01:
                return 'error'

            pitchedSample = ffmpeg.input('temp/samp1.webm').audio.filter('rubberband', pitch=rateFromPitch)
            out = ffmpeg.output(pitchedSample, f'temp/samp{i}.ogg')
            try:
                out.run()
            except:
                return 'error'



    async def renderYTPMV(self, notes, bpm):

        timelineV = []
        timelineA = []
        flipSwitch = 1
        timer = 0.0
        for i in range(len(notes)):

            try:
                length = float(notes[i].split('/')[1])*60/bpm
                pitch = notes[i].split('/')[0]
            except:
                return 'error'

            if pitch != '':

                audio = AudioFileClip(f'temp/samp{pitch}.ogg')
                clip = VideoFileClip(f"temp/samp{flipSwitch}.webm")

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
        for i in timelineV:
            i.close()

        for i in timelineA:
            i.close()

        final_Vclip.close()
        final_Aclip.close()



    async def saveAttachmentOrRef(self, message):

        #CHECK FOR ATTACHMENT
        if message.attachments == [] and message.reference == None:
            return

        #SAVE ORIGINAL SAMPLE
        if message.attachments != []:
            attachment = message.attachments[0]
        else:
            referencedMessage = await message.channel.fetch_message(message.reference.message_id)
            try:
                attachment = referencedMessage.attachments[0]
            except:
                return
        if not attachment.content_type.startswith('video'):
            return

        filename = 'sample_' + attachment.filename
        print(filename)
        file = open(f'./temp/{filename}', 'wb')
        await attachment.save(file)
        return filename



    async def trim(self, message):

        msgSplit = message.content.split(' ')
        try:
            start = msgSplit[2]
            end = msgSplit[3]
        except:
            return

        await message.add_reaction(emoji='⌚')

        filename = await self.saveAttachmentOrRef(message)
        if filename == None:
            return

        clip = VideoFileClip(f'./temp/{filename}')

        if float(end) > clip.duration:
            end = clip.duration

        clip = clip.subclip(start, end)

        clip.resize(width=420).write_videofile('./temp/trimmed.webm', codec=self.codec)


        #SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/trimmed.webm'))
        except:
            await message.reply('File too big, aborting...')

        #CLOSE CLIPS
        clip.close()



    async def volume(self, message):

        msgSplit = message.content.split(' ')
        try:
            volRate = float(msgSplit[2])
        except:
            return

        await message.add_reaction(emoji='⌚')

        filename = await self.saveAttachmentOrRef(message)
        if filename == None:
            return

        clip = VideoFileClip(f'./temp/{filename}')
        try:
            clip = clip.volumex(volRate)
        except:
            return

        clip.resize(width=420).write_videofile('./temp/volume.webm', codec=self.codec)

        #SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/volume.webm'))
        except:
            await message.reply('File too big, aborting...')

        #CLOSE CLIPS
        clip.close()


    async def add(self, message):

        if len(self.vidsToMerge) == 4:
            await message.reply('Limit for merging is 4. Send \'ytpmvbot reset\' to start over.')
            return

        try:
            referencedMessage = await message.channel.fetch_message(message.reference.message_id)
        except:
            return
            
        if referencedMessage.attachments == []:
            return

        self.vidsToMerge.append(referencedMessage)
        await referencedMessage.add_reaction(emoji='🎬')



    async def reset(self, message):
        self.vidsToMerge = []
        await message.add_reaction(emoji="👌")



    async def merge(self, message):

        await message.add_reaction(emoji='⌚')

        #RESET TEMP FOLDER
        self.clearTemp()
        
        counter = 0
        for i in self.vidsToMerge:
            attachment = i.attachments[0]
            file = open(f'./temp/merge{counter}', 'wb')
            await attachment.save(file)
            counter += 1

        tracks = []
        counter = 0
        for i in self.vidsToMerge:
            clip = VideoFileClip(f"./temp/merge{counter}")
            tracks.append(clip)
            counter += 1

        if len(self.vidsToMerge) == 2:
            final_clip = clips_array([tracks])

        elif len(self.vidsToMerge) == 4:
            top = tracks[:2]
            bottom = tracks[2:]

            final_clip = clips_array([top, bottom])
        else:
            await message.reply('Correct number of videos to merge is 2 or 4. Send \'ytpmvbot reset\' to start over.')
            return
        
        final_clip.resize(width=420).write_videofile(f'./temp/ytpmvmbot.webm', codec=self.codec)

        #SEND FILE TO DISCORD
        try:
            await message.reply(file=discord.File(f'./temp/ytpmvmbot.webm'))
        except:
            await message.reply('File too big, aborting...')

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


    if message.content.lower().startswith('ytpmvbot '):
        await ytpmv.addToQueue(message)



client.run(KEY)
