import argparse
import datetime
import math
import struct
import time
from pyaudio import PyAudio as pa
from pyaudio import paFloat32


class JJYsignal:
    """JJY signal emurator using python and pyaudio

    Attributes
    ----------
    duration : int
        duration of JJY signal output in sec.
    frequency : int
        frequency of signal tone,
        JJY wave of 40 kHz is generated as 3rd harmonic of 13.333k Hz.
    rate : int
        sampling rate
    dat : list
        60 data of -1, 0, or 1
    waves : list
        3 sine waves of the duration of 0.8, 0.5, and 0.2 seconds
    elaps : int
        elapsed time of execution

    Examples
    ----------
    To play 10 minutes JJY signal, execute the following command.
        $ python pyjjy.py -d 600
    or,
        >>> from pyjjy import JJYsignal
        >>> jj = JJYsignal(duration=600)
        >>> jj.play()
    """
    def __init__(
            self, samplerate=44100, frequency=13333, channels=1,
            chunk=1024, duration=float('inf')):
        """Constructor for JJYsignal, with defaults.

        Parameters
        ----------
        samplerate : int, default 44100
            sampling rate
        frequency : int, default 13333
            frequency of signal tone,
            JJY wave of 40 kHz is generated as 3rd harmonic of 13.333k Hz.
        channels : int, default 1
            number of channels
        chunk : int, default 1024
            specifies the number of frames per buffer
        duration : float, default infty
            duration of JJY signal output in sec.
        """

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
        """Reset dat list to empty.
        """
        self.dat = []

    def putdat(self, value):
        """Put one or multiple items to the dat list.

        Parameters
        ----------
        value : int or list
            One of (-1, 0, 1), or list of them
        """
        if type(value) is int:
            self.dat.append(value)
        else:
            self.dat.extend(value)

    def generate_wave(self):
        """Generate three audio signals as float32 byte arrays.

        Returns
        -------
        wvs : list
            List of signals corresponds to [0, 1, 'marker'].
            Lengths of the signales are [0.8, 0.5, 0.2] seconds.
        """
        wvs = []  # list of waves
        for width in [0.8, 0.5, 0.2]:
            _d = [math.sin(2 * math.pi * self.frequency * _i / self.rate)
                  for _i in range(0, int(self.rate * width))]
            raw = struct.pack('f'*len(_d), *_d)  # cast to float byte array
            wvs.append(raw)
        return wvs

    def update_seq(self, tim):
        """Generate signal sequence for this minute.

        Parameters
        ----------
        tim : datetime.datetime
            Time to convert JJY signal.
            'marker' signal is stored as -1.
        """

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
        """Set interval timer to call tone function.
        Exit if elapsed time >= duration.
        Send one pulse every 0 ms in a 50 us loop.
        """
        while self.elaps <= self.duration:
            time.sleep(1e-5)
            now = datetime.datetime.now()
            ms = now.microsecond // 1000.
            # if 0 ms comes, send a tone to the system.
            if not ms:
                self.tone(now.second)

    def tone(self, sec):
        """Send one-shot signal.

        Parameters
        ----------
        sec : int
            Second number to play.
            Minimum is 0, and maximum is 59.
        """
        value = self.dat[sec]  # -1, 0, or 1
        sound = self.waves[value]
        self.stream.write(sound)

        # Count up elapsed time
        self.elaps += 1

        # Update at every 0 second
        if sec == 0:
            self.update_seq(datetime.datetime.now())


def main():
    parser = argparse.ArgumentParser(
        description='JJY signal emurator using python and pyaudio')

    parser.add_argument('-r', '--samplerate', type=int, help='sampling rate')
    parser.add_argument('-f', '--frequency', type=int, help='tone frequency')
    parser.add_argument('-d', '--duration', type=int, help='run duration')

    args = parser.parse_args()

    jj = JJYsignal(**{k: v for k, v in vars(args).items() if v is not None})
    jj.play()


if __name__ == '__main__':
    # execute with python -m pyjjy
    main()
