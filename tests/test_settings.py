import unittest

from video2midi.settings import *
from video2midi.prefs import prefs

class TestMySettings(unittest.TestCase):

    def test_a_settings_load(self):
        self.assertEqual(prefs.xoffset_whitekeys, 60)
        loadsettings('./tests/spin.mp4.ini')
        self.assertEqual(prefs.xoffset_whitekeys, 99)

    def test_b_compatible_size(self):
        loadsettings('vidSpin/spin.mp4.ini')
        self.assertEqual(len(prefs.keyp_colors_channel_prog),14);

        colorBtns = []
        for i in range(22):
            colorBtns.append( [0,0,0] )

        compatibleColors(colorBtns)
        self.assertEqual(len(prefs.keyp_colors_channel_prog),22);

if __name__ == '__main__':
    unittest.main()