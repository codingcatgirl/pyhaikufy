import re
import string
import typing

import pyphen


overrides_de = {
    'idee': 'i-dee',
    'software': 'soft-ware',
    'hardware': 'hard-ware',
    'update': 'up-date',
    'upgrade': 'up-grade',
}
for c in string.ascii_lowercase+'öäüß':
    overrides_de[c] = 'yp-si-lon' if c == 'y' else c

join_syllables_de = ('ti-on', 'ti-ons', 'nai-v', 'ge-ht')
split_syllables_de = ('na-iv', 'de-o', 'de-os', 'pi-a', 'o-dy')


def german_number_syllables(number):
    if number < 10:
        return 2 if number == 7 else 1
    if number < 100:
        if number < 13:
            return 1
        result = 0
        if number % 10:
            result += german_number_syllables(number % 10)
            if number > 20:
                result += 1
        result += 1 if number//10 == 1 else 2
        return result
    if number < 1000:
        result = german_number_syllables(number // 100) + 2
        if number % 100:
            result += german_number_syllables(number % 100)
        return result
    if number < 1000000:
        result = german_number_syllables(number // 1000) + 2
        if number % 1000:
            result += german_number_syllables(number % 1000)
        return result
    return None


class Haikufy:
    def __init__(self, lang='de_DE', letters=string.ascii_letters+'äöüÄÖÜßẞ', ignore_chars="'", split_chars='-/',
                 consonants='bcdfghjjklmnpqrstvwxyzß', overrides=overrides_de,
                 number_syllables=german_number_syllables, join_syllables=join_syllables_de,
                 split_syllables=split_syllables_de, vocals='aeiouäöü'):
        self.dic = pyphen.Pyphen(lang=lang, left=1, right=1)
        self.letters = letters
        self.ignore_chars = ignore_chars
        self.split_chars = split_chars
        self.consonants = consonants
        self.overrides = overrides
        self.number_syllables = number_syllables
        self.join_syllables = join_syllables
        self.split_syllables = split_syllables
        self.vocals = vocals

    def haikufy(self, text: str) -> typing.Optional[str]:
        if not text:
            return None
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

    def count_syllables(self, word: str) -> typing.Optional[int]:
        while word and word[0] not in self.letters+string.digits:
            word = word[1:]
        while word and word[-1] not in self.letters+string.digits:
            word = word[:-1]
        if not word:
            return 0

        if word.isdigit() and self.number_syllables is not None:
            return self.number_syllables(int(word))

        for char in self.split_chars:
            word = word.replace(char, ' ')
        for char in self.ignore_chars:
            word = word.replace(char, '')

        for char in word:
            if char != ' ' and char not in self.letters:
                return None

        subwords = word.split()
        for subword in subwords:
            if len(subword) == 1 and subword.lower() not in self.overrides:
                return None

        return sum((self._count_subword_syllables(w) for w in subwords), 0)

    def _count_subword_syllables(self, w):
        inserted = self.overrides.get(w.lower())
        if inserted is not None:
            return len(inserted.split('-'))

        inserted = '-'+self.dic.inserted(w.lower())+'-'
        while True:
            new = re.sub(r'(['+self.vocals+']+)(['+self.consonants+']?)(['+self.consonants+']+)(['+self.vocals+']+)',
                         r'\1\2-\3\4', inserted)
            if new == inserted:
                break
            inserted = new
        inserted = re.sub(r'^-(['+self.consonants+'])-([^-])', r'-\1\2', inserted)
        inserted = re.sub(r'-(['+self.consonants+'])-', r'\1-', inserted)
        for join_syllables in self.join_syllables:
            inserted = inserted.replace('-'+join_syllables+'-', '-'+join_syllables.replace('-', '')+'-')
        for split_syllables in self.split_syllables:
            inserted = inserted.replace('-'+split_syllables.replace('-', '')+'-', '-'+split_syllables+'-')
        return max(len(inserted[1:-1].split('-')), 1)


if __name__ == '__main__':
    haikufy = Haikufy()

    while True:
        text = input('>>> ')
        haiku = haikufy.haikufy(text)
        if haiku is None:
            print('Not a haiku!')
            continue
        print(haiku)
