import string
import typing

import pyphen


overrides_de = {
    'einen': 'ei-nen',
    'naiv': 'na-iv',
    'tweets': 'tweets',
}


class Haikufy:
    def __init__(self, lang='de_DE', letters=string.ascii_letters+'äöüÄÖÜßẞ', ignore_chars="'", split_chars='-',
                 forbidden_oneletter_syllables='bcdfghjjklmnpqstvwxyz', overrides=overrides_de):
        self.dic = pyphen.Pyphen(lang=lang, left=1, right=1)
        self.letters = letters
        self.ignore_chars = ignore_chars
        self.split_chars = split_chars
        self.forbidden_oneletter_syllables = forbidden_oneletter_syllables
        self.overrides = overrides

    def haikufy(self, text: str) -> typing.Optional[str]:
        words, syllables = zip(*((word, self.count_syllables(word)) for word in text.split()))
        print(words, syllables)
        if None in syllables or sum(syllables) != 17:
            return None

        words, syllables = list(words), list(syllables)

        lines = []
        for target_syllables in (5, 7, 5):
            line = []
            line_syllables = 0
            while syllables and line_syllables+syllables[0] <= target_syllables:
                line.append(words.pop(0))
                line_syllables += syllables.pop(0)
            if line_syllables != target_syllables:
                return None
            lines.append(' '.join(line))

        return '\n'.join(lines)

    def _allowed_syllable(self, s):
        return len(s) > 1 or s not in self.forbidden_oneletter_syllables

    def count_syllables(self, word: str) -> typing.Optional[int]:
        if word.isdigit():
            return None

        while word and word[0] not in self.letters+string.digits:
            word = word[1:]
        while word and word[-1] not in self.letters+string.digits:
            word = word[:-1]
        if not word:
            return 0

        if word.isdigit():
            return None

        for char in self.split_chars:
            word = word.replace(char, ' ')
        for char in self.ignore_chars:
            word = word.replace(char, '')

        for char in word:
            if char != ' ' and char not in self.letters:
                return None

        subwords = word.split()
        for subword in subwords:
            if len(subword) == 1:
                return None

        return sum((max(
            len(tuple(s for s in self.overrides.get(w.lower(), self.dic.inserted(w)).split('-')
                      if self._allowed_syllable(s))), 1)
            for w in subwords
        ), 0)


if __name__ == '__main__':
    haikufy = Haikufy()

    while True:
        text = input('>>> ')
        haiku = haikufy.haikufy(text)
        if haiku is None:
            print('Not a haiku!')
            continue
        print(haiku)
