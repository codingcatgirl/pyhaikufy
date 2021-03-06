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
    'facebook': 'face-book',
    'interface': 'in-ter-face',
    'interfaces': 'in-ter-faces',
    'online': 'on-line',
    'offline': 'off-line',
    'home': 'home',
    'office': 'of-fice',
    'homeoffice': 'home-of-fice',
    'image': 'i-ma-ge',
    '34c3': 'vier-und-drei-ßig-c-drei',
    'miyuuli': 'mi-yuu-li',
    'stripe': 'stripe',
    'deadname': 'dead-name',
    'deadnames': 'dead-names',
    'fea-ture': 'fea-ture',
    'fea-tures': 'fea-tures',
    'ipv4': 'i-p-v-4',
    'ipv6': 'i-p-v-6',
    'yeah': 'yeah',
    'where': 'whe-re',
    'fullhd': 'full-h-d',
    'ios': 'i-os',
    'cdu': 'c-d-u',
    'csu': 'c-s-u',
    'afd': 'a-f-d', # others not needed as they are consonants only
    'device': 'de-vice',
    'nope': 'nope',
}
for c in string.ascii_lowercase+'öäüß':
    overrides_de[c] = 'yp-si-lon' if c == 'y' else c

replaces_de = {
    '€': ' Euro ',
    '$': ' Dollar ',
    'z.B.': ' zum Beispiel ',
    'z.b.': ' zum Beispiel ',
}

join_syllables_de = ('ti-on', 'ti-ons', 'si-on', 'si-ons', 'nai-v', 'ge-ht', 'ed-ge', 'kin-ky', 'zi-ell', 'zi-el',
                     'wi-ngs', 'no-te-book', 'mo-bi-le', 'in-dia')
split_syllables_de = ('na-iv', 'de-o', 'de-os', 'pi-a', 'o-dy', 'o-nym', 'o-ny', 'pro-xy', 'note-book', 'mo-bile'
                      'in-di-a', 'bi-o', 'see-ot')
no_syllable_start_de = ('bb', 'bc', 'bd', 'bp', 'cm', 'cn', 'cv', 'cw', 'cx',
                        'db', 'dc', 'df', 'dg', 'dh', 'dj', 'dk', 'dl', 'dm', 'dn', 'dp', 'dq', 'dz',
                        'gb', 'gc', 'gd', 'gf', 'gj', 'gk', 'gq'
                        'kg', 'kq',
                        'lr', 'lv',
                        'ml',
                        'nl'
                        'pb', 'pm', 'pn',
                        'qb', 'qc', 'qd', 'qf', 'qg', 'qh', 'qj', 'qk', 'ql', 'qm', 'qn', 'qp', 'qr',
                        'qs', 'qt', 'qv', 'qw', 'qx', 'qy', 'qz'
                        'tb', 'td', 'tf', 'tg', 'tn', 'tm',
                        'xg', 'xk', )
no_syllable_end_de = ('bm', 'bn', 'bp', 'cm', 'cn', 'cv', 'cw', 'cx',
                      'db', 'dc', 'df', 'dg', 'dh', 'dj', 'dk', 'dl', 'dm', 'dn', 'dp', 'dq', 'dz',
                      'fm',
                      'gb', 'gc', 'gd', 'gf', 'gj', 'gk', 'gq'
                      'kg', 'kq',
                      'lr',
                      'ml',
                      'nl'
                      'pb', 'pm', 'pn',
                      'qb', 'qc', 'qd', 'qf', 'qg', 'qh', 'qj', 'qk', 'ql', 'qm', 'qn', 'qp', 'qr',
                      'qs', 'qt', 'qv', 'qw', 'qx', 'qy', 'qz'
                      'tb', 'td', 'tf', 'tg', 'tn', 'tm',
                      'xg', 'xk', )
emoticons = ('xd', 'xf', 'm(', 'm)', '\\o/', '/o\\', ':d', ':3', '<3', 'o.o', 'o_o', 'q.q', 'q_q', '/o/', '\\o\\', ':o')


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
    def __init__(self, lang='de_DE', letters=string.ascii_letters+'äöüÄÖÜßẞ', ignore_chars="'*", split_chars='-/_',
                 consonants='bcdfghjklmnpqrstvwxyzß', replaces=replaces_de, overrides=overrides_de,
                 number_syllables=german_number_syllables, join_syllables=join_syllables_de,
                 split_syllables=split_syllables_de, vocals='aeiouäöü',
                 abbr_pattern=r'^[bcdfghjklmnpqrstvwxzß]+$', emoticons=emoticons,
                 no_syllable_start=no_syllable_start_de, no_syllable_end=no_syllable_end_de):
        self.dic = pyphen.Pyphen(lang=lang, left=1, right=1)
        self.letters = letters
        self.ignore_chars = ignore_chars
        self.split_chars = split_chars
        self.consonants = consonants
        self.replaces = replaces
        self.overrides = overrides
        self.number_syllables = number_syllables
        self.join_syllables = join_syllables
        self.split_syllables = split_syllables
        self.vocals = vocals
        self.abbr_pattern = abbr_pattern
        self.emoticons = emoticons
        self.no_syllable_start = no_syllable_start
        self.no_syllable_end = no_syllable_end

    def haikufy(self, text: str) -> typing.Optional[str]:
        if not text:
            return None

        for before, after in self.replaces.items():
            text = text.replace(before, after)

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
        if word.lower() in self.emoticons:
            return 0
        while word and word[0] not in self.letters+string.digits:
            word = word[1:]
        while word and word[-1] not in self.letters+string.digits:
            word = word[:-1]
        if not word:
            return 0

        if word.isdigit() and self.number_syllables is not None:
            return self.number_syllables(int(word))

        if re.match(self.abbr_pattern, word.lower()):
            if not (word.isupper() or word.islower()):
                return None
            word = '-'.join(word)

        for char in self.split_chars:
            word = word.replace(char, ' ')
        for char in self.ignore_chars:
            word = word.replace(char, '')

        inserted = self.overrides.get(word.lower())
        if inserted is not None:
            return len(inserted.split('-'))

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
        for vocal in self.vocals:
            inserted = re.sub(r'^-'+vocal+r'(-'+vocal+r')+', '-'+vocal+vocal, inserted)
            inserted = re.sub(vocal+r'(-'+vocal+r')+-$', vocal+vocal+'-', inserted)
        for no_syllable_start in self.no_syllable_start:
            inserted = re.sub(r'-'+no_syllable_start+'([^-])', r'-'+'-'.join(no_syllable_start)+r'\1', inserted)
        for no_syllable_end in self.no_syllable_end:
            inserted = re.sub(r'([^-])'+no_syllable_end+'-', r'\1'+'-'.join(no_syllable_end)+r'-', inserted)
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
