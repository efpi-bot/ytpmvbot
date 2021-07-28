import ffmpeg
import os
import shutil
from moviepy.editor import *
import discord


class ytpmv:

	def __init__(self):
		None


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
			try:
				int(notePitch)
			except:
				await message.reply('wrong usage, aborting...')
				return
			if notePitch != '' and int(notePitch) not in uniqueNotes:
				uniqueNotes.append(int(notePitch))

		for i in uniqueNotes:
			pitchedSample = ffmpeg.input('samp1.mp4').audio.filter('rubberband', pitch=2**(i/12))
			out = ffmpeg.output(pitchedSample, f'assets/samp{i}.mp3')
			out.run()


		timelineV = []
		timelineA = []
		flipSwitch = 1
		timer = 0.0
		for i in range(len(notes)):

			length = float(notes[i].split('/')[1])*60/bpm
			pitch = notes[i].split('/')[0]


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

			timer += length
			flipSwitch *= -1

			timelineV.append(clip)
			timelineA.append(audio)

		final_Vclip = CompositeVideoClip(timelineV)
		final_Aclip = CompositeAudioClip(timelineA)
		final_Vclip.audio = final_Aclip
		final_Vclip.resize(width=420).write_videofile("ytpmvbot.mp4")

		await message.reply(file=discord.File('ytpmvbot.mp4'))


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

    if message.content.lower().startswith('ytpmvbot '):
        await ytpmv.run(message)


client.run(KEY)
