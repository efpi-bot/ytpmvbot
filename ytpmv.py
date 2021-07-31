import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord



class ytpmv:

	def __init__(self):
		self.queue = []
		self.mergeQueue = []
		self.fileNames = []
		self.idNum = 0

	async def renderFlippedVid(self,filename):

		if os.path.exists('assets'):
			shutil.rmtree('assets')

		os.mkdir('assets')


		inVid = ffmpeg.input(filename)
		inFlipVid = inVid.video.hflip()

		outVid = ffmpeg.output(inVid, 'assets/samp1.mp4')
		outVid.run()

		outFlip = ffmpeg.output(inFlipVid, 'assets/samp-1.mp4')
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
			pitchedSample = ffmpeg.input('assets/samp1.mp4').audio.filter('rubberband', pitch=2**(i/12))
			out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
			out.run()


	async def renderYTPMV(self, notes, bpm):

		timelineV = []
		timelineA = []
		flipSwitch = 1
		timer = 0.0
		for i in range(len(notes)):

			length = float(notes[i].split('/')[1])*60/bpm
			pitch = notes[i].split('/')[0]

			if pitch != '':

				audio = AudioFileClip(f'assets/samp{pitch}.mp3')
				clip = VideoFileClip(f"assets/samp{flipSwitch}.mp4")

				clip.start = timer
				audio.start = timer

				if length < clip.duration:
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

		final_Vclip.resize(width=420).write_videofile(f"ytpmvbot{self.idNum}.mp4")

		#CLOSE CLIPS
		for i in timelineV:
			i.close()

		for i in timelineA:
			i.close()

		final_Vclip.close()
		final_Aclip.close()


	async def run(self, message):
		if message.attachments == []:
			return

		bpm = 120
		content = message.content
		if len(content.split('-bpm')) == 2:
			try:
				bpm = int(content.split('-bpm')[1])
			except:
				None
			content = content.split('-bpm')[0].rstrip()

		notes = content[9:].split(' ')
		print(notes)

		attachment = message.attachments[0]
		filename = attachment.filename
		print(filename)
		file = open(f'./{filename}', 'wb')
		await attachment.save(file)

		#RENDER HFLIP
		await self.renderFlippedVid(filename)

		#RENDER PITCHED SAMPLES
		if await self.renderPitchedSamples(notes) == 'error':
			await message.reply('wrong pitch value, aborting...')
			return


		#RENDER YTPMV
		await self.renderYTPMV(notes, bpm)

		await message.reply(file=discord.File(f'ytpmvbot{self.idNum}.mp4'))
		self.idNum += 1


	async def merge(self, message):
		
		for i in self.mergeQueue:
			attachment = i.attachments[0]
			filename = attachment.filename
			file = open(f'./merge/{filename}', 'wb')
			await attachment.save(file)
			self.fileNames.append(filename)

		tracks = []
		for i in self.fileNames:
			clip = VideoFileClip(f"./merge/{i}")
			tracks.append(clip)


		if len(self.mergeQueue) == 2:
			final_clip = clips_array([tracks])

		elif len(self.mergeQueue) == 4:
			top = tracks[:2]
			bottom = tracks[2:]

			final_clip = clips_array([top, bottom])
		else:
			await message.reply('Correct number of videos to merge is 2 or 4. Send \'ytpmvbot reset\' to start over.')
			return
		
		final_clip.resize(width=420).write_videofile(f"ytpmvmerged{self.idNum}.mp4")

		await message.reply(file=discord.File(f'ytpmvmerged{self.idNum}.mp4'))
		self.idNum += 1
		await self.reset()

	async def add(self, message):
		if len(self.mergeQueue) == 4:
			await message.reply('Limit for merging is 4. Send \'ytpmvbot reset\' to start over.')
			return
		referencedMessage = await message.channel.fetch_message(message.reference.message_id)
		self.mergeQueue.append(referencedMessage)
		await referencedMessage.add_reaction(emoji='🎬')

	async def reset(self):
		self.mergeQueue = []
		self.fileNames = []


	async def manageQueue(self):
		if self.queue == []:
			return

		currentMessage = self.queue[0]

	    if currentMessage.content.lower() == 'ytpmvbot add':
	    	await self.add(message)

	    elif currentMessage.content.lower() == 'ytpmvbot merge':
	    	await self.merge(message)

	    elif currentMessage.content.lower() == 'ytpmvbot reset':
	    	await self.reset()

	    elif currentMessage.content.lower().startswith('ytpmvbot '):
	    	await self.run(currentMessage)


	async def addToQueue(self, message):
		self.queue.append(message)
		if message == self.queue[0]:
			await self.manageQueue()


#DISCORD BOT HERE

KEY = open('./key').read()
client = discord.Client()
ytpmv = ytpmv()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.lower().startswith('ytpmvbot '):
        await ytpmv.addToQueue(message)

client.run(KEY)
