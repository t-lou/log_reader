import re


class Filter:
    def __init__(self, settings: list[dict], all_match: bool) -> None:
        self._all_match = all_match
        self._compiled = []

        for s in settings:
            keyword = s["keyword"]
            if s["reg"]:
                # Precompile regex once
                pattern = re.compile(keyword)
                self._compiled.append(lambda line, p=pattern: bool(p.search(line)))
            else:
                # Pre-store substring for fast lookup
                self._compiled.append(lambda line, k=keyword: k in line)

    def match(self, line: str) -> bool:
        matcher = all if self._all_match else any
        return matcher(fn(line) for fn in self._compiled)
