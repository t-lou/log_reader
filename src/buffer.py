from collections import deque


class Buffer:
    def __init__(self, capacity: int, save_first: bool):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        self.save_first = save_first

        if save_first:
            # store first N items → stop accepting after full
            self._data = []
            self._full = False
        else:
            # store last N items → use deque for efficiency
            self._data = deque(maxlen=capacity)

    def add(self, item):
        if self.save_first:
            if not self._full:
                self._data.append(item)
                self._full = len(self._data) >= self.capacity
            # ignore new items once full
        else:
            # deque automatically drops old items
            self._data.append(item)

    def get(self):
        """Return the stored items as a list."""
        if self.save_first:
            return list(self._data)
        else:
            return list(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Buffer(capacity={self.capacity}, save_first={self.save_first}, data={self.get()})"
