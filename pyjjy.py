import argparse
import datetime
import math
import signal
import struct
import time
from pyaudio import PyAudio as pa
from pyaudio import paFloat32


class JJYsig:
    '''JJY emurator using python and pyaudio'''
    def __init__(
            self, samplerate=44100, frequency=13333, channels=1,
            chunk=1024, duration=float('inf')):
        '''Constructor for JJYsig, with defaults.

        Parameters
        ----------
        samplerate : float, default 44100
            sampling rate
        frequency : float, default 13333
            frequency of signal tone,
            JJY wave of 40 kHz is generated as 3rd harmonic of 13.333k Hz.
        channels : int, default 1
            number of channels
        chunk : int, default 1024
            specifies the number of frames per buffer
        duration : float, default infty
            duration of JJY signal output in sec.
        '''

        self.duration = duration
        self.frequency = frequency
        self.dat = []
        self.rate = samplerate
        self.elaps = 1
        self.waves = self.generate_wave()
        self.stream = pa().open(
            format=paFloat32, channels=channels,
            rate=self.rate, frames_per_buffer=chunk, output=True
        )
        # Initial signal sequence update
        self.update_seq(datetime.datetime.now())

    def reset(self):
        '''Reset dat list to empty.'''
        self.dat = []

    def putdat(self, value):
        '''Put one or multiple items to the dat list.'''
        if type(value) is int:
            self.dat.append(value)
        else:
            self.dat.extend(value)

    def generate_wave(self):
        '''Generate three audio signals as float32 byte arrays'''
        wvs = []  # list of waves
        for width in [0.8, 0.5, 0.2]:
            _d = [math.sin(2 * math.pi * self.frequency * _i / self.rate)
                  for _i in range(0, int(self.rate * width))]
            print(_d)
            raw = struct.pack('f'*len(_d), *_d)  # cast to float byte array
            wvs.append(raw)
        return wvs

    def update_seq(self, tim):
        '''Generate signal sequence for this minute.'''

        self.reset()

        # Starting marker
        self.putdat(-1)

        # Minutes
        arr_m010 = [int(x) for x in format(tim.minute // 10, '03b')]
        arr_m001 = [int(x) for x in format(tim.minute % 10, '04b')]
        self.putdat(arr_m010 + [0, ] + arr_m001)

        # 9th - 11th seconds
        self.putdat([-1, 0, 0])

        # Hours
        arr_h010 = [int(x) for x in format(tim.hour // 10, '02b')]
        arr_h001 = [int(x) for x in format(tim.hour % 10, '04b')]
        self.putdat(arr_h010 + [0, ] + arr_h001)

        # 19th - 21st seconds
        self.putdat([-1, 0, 0])

        # Days
        startofyear = datetime.date(tim.year, 1, 1).toordinal()
        day = tim.toordinal() - startofyear + 1
        arr_d100 = [int(x) for x in format(day // 100, '02b')]
        arr_d010 = [int(x) for x in format((day % 100) // 10, '04b')]
        arr_d001 = [int(x) for x in format(day % 10, '04b')]
        self.putdat(arr_d100 + [0, ] + arr_d010 + [-1] + arr_d001 + [0, 0])

        # Parities
        pa1 = sum(arr_h010 + arr_h001) % 2
        pa2 = sum(arr_m010 + arr_m001) % 2
        self.putdat([pa1, pa2])

        # 38th - 40th seconds
        self.putdat([0, -1, 0])

        # Years
        arr_y10 = [int(x) for x in format((tim.year % 100) // 10, '04b')]
        arr_y01 = [int(x) for x in format(tim.year % 10, '04b')]
        self.putdat(arr_y10 + arr_y01)

        # 49th seconds
        self.putdat(-1)

        # Day of week
        wday = tim.isoweekday() % 7
        arr_wday = [int(x) for x in format(wday, '03b')]
        self.putdat(arr_wday)

        # Leap second
        self.putdat([0, 0])

        # Last
        self.putdat([0, 0, 0, 0, -1])

    def play(self):
        '''Set interval timer to call tone function.'''
        signal.signal(signal.SIGALRM, self.tone)
        now = datetime.datetime.now()
        wait = 1.0 - now.microsecond / 1e6
        intv = 1.0
        signal.setitimer(signal.ITIMER_REAL, wait, intv)
        while True:
            time.sleep(100)  # dummy run

    def exit(self):
        '''Exit execution.'''
        exit(0)

    def tone(self, *args):
        '''Send one-shot signal.'''
        now = datetime.datetime.now()
        value = self.dat[now.second]  # -1, 0, or 1
        sound = self.waves[value]
        self.stream.write(sound)

        # Exit excecution if specified time has passed
        if self.elaps >= self.duration:
            self.exit()
        self.elaps += 1

        # Update at every 0 second
        if now.second == 0:
            self.update_seq(now)


def main():
    parser = argparse.ArgumentParser(
        description='JJY emurator using python and pyaudio')

    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
    parser.add_argument('-f', '--frequency', type=int, help='tone frequency')
    parser.add_argument('-d', '--duration', type=int, help='run duration')

    args = parser.parse_args()

    jj = JJYsig(**{k: v for k, v in vars(args).items() if v is not None})
    jj.play()


if __name__ == '__main__':
    main()
