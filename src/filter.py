import re


class Filter:
    def __init__(self, settings, all_match):
        self._all_match = all_match
        self.substrings = []
        self.regexes = []

        for s in settings:
            if s["reg"]:
                self.regexes.append(re.compile(s["keyword"]).search)
            else:
                self.substrings.append(s["keyword"])

    def match(self, line):
        if self._all_match:
            # all must match
            for sub in self.substrings:
                if sub not in line:
                    return False
            for reg in self.regexes:
                if not reg(line):
                    return False
            return True
        else:
            # any must match
            for sub in self.substrings:
                if sub in line:
                    return True
            for reg in self.regexes:
                if reg(line):
                    return True
            return False
