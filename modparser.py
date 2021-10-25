import json
import sys


class mod:
    def __init__(self, filename):

        self.notesToInts = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
        self.channels = []

        mod_dump = open(filename).read()
        rows_arr = []

        for i in mod_dump.split('\n'):
            if i.startswith('|'):
                rows_arr.append(i)

        channel_count = len(rows_arr[0].split('|')) - 1
        for i in range(channel_count):
            self.channels.append({'name': f'channel {i}', 'instruments': {}})

        # CREATE CHANNEL ARRAYS
        channel_arr = [[] for _ in range(channel_count)]
        for i in range(len(rows_arr)):
            row_split_arr = rows_arr[i].split('|')[1:]

            for channel in range(channel_count):
                note = row_split_arr[channel][:3]

                if note == '===':
                    pitch = '==='
                else:
                    try:
                        pitch = self.notesToInts[note[0]]

                        if note[1] == '#':
                            pitch += 1
                        elif note[1] == 'b':
                            pitch -= 1
                        pitch += (int(note[2]) - 4) * 12

                    except:
                        pitch = ''

                instrument = row_split_arr[channel][3:5]
                channel_arr[channel].append({'note': pitch, 'instr': instrument})

        # SPLIT INSTRUMENTS
        for channel in channel_arr:
            for n in range(len(channel)):

                pitch = channel[n]['note']
                instrument = channel[n]['instr']

                if n == 0:
                    last_instrument = instrument

                # print(pitch, instrument)
                current_channel = channel_arr.index(channel)

                # WELL THIS IS UGLY IM SRY
                if (
                    instrument != '..'
                    and instrument not in self.channels[current_channel]['instruments']
                ):
                    self.channels[current_channel]['instruments'][str(instrument)] = []
                    self.channels[current_channel]['instruments'][
                        str(instrument)
                    ].extend(list([''] * n))

                if instrument == '..':
                    for _ in self.channels[current_channel]['instruments']:
                        if pitch != '===':
                            self.channels[current_channel]['instruments'][_].append('')
                        else:
                            self.channels[current_channel]['instruments'][_].append(
                                '==='
                            )
                else:
                    for _ in self.channels[current_channel]['instruments']:
                        if instrument == _:
                            self.channels[current_channel]['instruments'][_].append(
                                pitch
                            )
                        else:
                            if instrument != last_instrument:
                                self.channels[current_channel]['instruments'][_].append(
                                    '==='
                                )
                            else:
                                self.channels[current_channel]['instruments'][_].append(
                                    ''
                                )

                last_instrument = instrument

        # OK NOW FINAL PARSE I GUESS
        # MY HEAD HURTS
        # print(self.channels[2])

        for channel in self.channels:
            for instrument in channel['instruments']:
                # print(channel['instruments'][instrument])

                current_note = ''
                last_note = 'start'
                duration = 1

                temp_pattern_list = []
                counter = 0
                for note in channel['instruments'][instrument]:
                    counter += 1
                    # print(note)

                    if last_note == 'start':
                        last_note = note

                    elif note == '':
                        duration += 1

                    elif note == '===':
                        temp_pattern_list.append(f'{last_note}/{duration/8}')
                        last_note = ''
                        duration = 1

                    else:
                        temp_pattern_list.append(f'{last_note}/{duration/8}')
                        last_note = note
                        duration = 1

                    if counter == len(channel['instruments'][instrument]):
                        temp_pattern_list.append(f'{last_note}/{duration/8}')
                        # print('end')

                pattern = ' '.join(temp_pattern_list)
                channel['instruments'][instrument] = pattern

        # print(self.channels)

        file = open('./mod_to_bot.json', 'w')
        jsonfile = json.dumps(self.channels, sort_keys=True, indent=4)
        file.write(jsonfile)
        file.close()

        print('ok! check mod_to_bot.json file')


myMod = mod(sys.argv[1])
