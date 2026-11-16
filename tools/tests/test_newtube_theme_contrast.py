"""Check TV theme text and focus contrast against the shipped palette roles."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COLORS = ROOT / 'smarttubetv/src/main/res/values/newtube_theme_colors.xml'
THEMES = ('reading', 'paper', 'graphite', 'midnight', 'dusk', 'light', 'dark', 'amber')


def rgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def luminance(color):
    channels = [c / 255 for c in color]
    channels = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in channels]
    return sum(c * weight for c, weight in zip(channels, (.2126, .7152, .0722)))


def contrast(a, b):
    low, high = sorted((luminance(a), luminance(b)))
    return (high + .05) / (low + .05)


class ThemeContrastTest(unittest.TestCase):
    def test_text_and_focus_contrast(self):
        colors = {item.attrib['name']: rgb(item.text) for item in ET.parse(COLORS).getroot()}
        for theme in THEMES:
            with self.subTest(theme=theme):
                get = lambda role: colors[f'newtube_{theme}_{role}']
                foreground = get('text')
                for surface in ('background', 'sidebar', 'card', 'selected'):
                    self.assertGreaterEqual(contrast(foreground, get(surface)), 4.5, surface)
                faded = tuple(round(.8 * f + .2 * b) for f, b in zip(foreground, get('sidebar')))
                self.assertGreaterEqual(contrast(faded, get('sidebar')), 4.5, 'unselected navigation')
                self.assertGreaterEqual(contrast(get('accent'), get('selected')), 3, 'focus outline')


if __name__ == '__main__':
    unittest.main()
