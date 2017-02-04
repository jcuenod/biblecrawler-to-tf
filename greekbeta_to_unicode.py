# completely ripped from https://github.com/ninjaaron/betacode/blob/master/betacode/greek.py
# so credit to ninjaaron again
from __future__ import unicode_literals
import re
from unicodedata import normalize as un

beta = r"abgdevzhqiklmncoprstufxyw"
greek = "αβγδεϝζηθικλμνξοπρστυφχψω"
sub_d = dict(zip(beta, greek))
sub_d.update(zip(beta.upper(), greek.upper()))
beta_diacritics = r")(|/\=+:&'#"
greek_diacritics = " ̓ ̔ ͅ ́ ̀ ͂ ̈· ̄ ̆ʹ".replace(' ', '')
sub_d.update(zip(beta_diacritics, greek_diacritics))
pass_through = set(' .,;-\t\n1234567890')

_dialytika = re.compile(r"([a-z])([()|/\\=&']+)\+")
_caps = re.compile(r"\*([()|/\\=+&']*)([a-z])")


def _capitalize(match):
    return match.group(2).upper() + match.group(1)


class BetacodeError(Exception):
    """Wrapper for KeyErrors that arise from invalid betacode."""
    def __init__(self, input_, error):
        self.input_ = input_
        self.error = error
    def __str__(self):
        return "failed decoding {} at '{}'".format(self.input_, self.error)


def _sigmas(decoded):
    if len(decoded) == 0:
        return
    if decoded[-1] == 'σ':
        decoded[-1] = 'ς'


def gk_decode(betacode):
    """betacode decoder optimized for single words, like, in loops."""
    betacode = betacode.lower()
    if '*' in betacode:
        betacode = _caps.sub(_capitalize, betacode)
    if '+' in betacode:
        betacode = _dialytika.sub(r'\1+\2', betacode)
    decoded = []
    for char in betacode:
        try:
            decoded.append(sub_d[char])
        except KeyError:
            if char in pass_through:
                _sigmas(decoded)
                decoded.append(char)
            else:
                raise BetacodeError(betacode, char)
    _sigmas(decoded)
    return un('NFKC', ''.join(decoded))
