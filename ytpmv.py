import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord
from random import randint


class ytpmv:

	def __init__(self):
		self.mergeQueue = []
		self.fileNames = []



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

		final_clip = clips_array([tracks])
		final_clip.resize(width=420).write_videofile("ytpmvmerged.mp4")

		await message.reply(file=discord.File('ytpmvmerged.mp4'))
		self.reset()

	async def add(self, message):
		referencedMessage = await message.channel.fetch_message(message.reference.message_id)
		self.mergeQueue.append(referencedMessage)
		await referencedMessage.add_reaction(emoji='🎬')

	async def reset(self):
		self.mergeQueue = []
		self.fileNames = []


	async def run(self, message):
		# if message.attachments == []:
			# return

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


		if os.path.exists('assets'):
			shutil.rmtree('assets')
		os.mkdir('assets')


		inVid = ffmpeg.input(filename)
		inFlipVid = inVid.video.hflip()

		outVid = ffmpeg.output(inVid, 'assets/samp1.mp4')
		outVid.run()

		outFlip = ffmpeg.output(inFlipVid, 'assets/samp-1.mp4')
		outFlip.run()



		uniqueNotes = []
		for i in notes:
			notePitch = i.split('/')[0]

			if notePitch == '':
				continue

			try:
				int(notePitch)
			except:
				await message.reply('wrong usage, aborting...')
				return
			if notePitch != '' and int(notePitch) not in uniqueNotes:
				uniqueNotes.append(int(notePitch))

		for i in uniqueNotes:
			pitchedSample = ffmpeg.input('assets/samp1.mp4').audio.filter('rubberband', pitch=2**(i/12))
			out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
			out.run()


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
					audio.end = timer+clip.duration

				flipSwitch *= -1

				timelineV.append(clip)
				timelineA.append(audio)

			timer += length

		final_Vclip = CompositeVideoClip(timelineV)
		final_Aclip = CompositeAudioClip(timelineA)
		final_Vclip.audio = final_Aclip
		randomNum = randint(1,1000)
		final_Vclip.resize(width=420).write_videofile(f"ytpmvbot{randomNum}.mp4")

		await message.reply(file=discord.File(f'ytpmvbot{randomNum}.mp4'))


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


    if message.content.lower() == 'ytpmvbot add':
    	await ytpmv.add(message)

    elif message.content.lower() == 'ytpmvbot merge':
    	await ytpmv.merge(message)

    elif message.content.lower() == 'ytpmvbot reset':
    	await ytpmv.reset()

    elif message.content.lower().startswith('ytpmvbot '):
        await ytpmv.run(message)

client.run(KEY)
