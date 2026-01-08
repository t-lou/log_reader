from collections import deque


class Buffer:
    def __init__(self, capacity: int, save_first: bool):
        """
        A small utility buffer that stores either:
        - the first `capacity` items (save_first=True), or
        - the last `capacity` items (save_first=False).

        Parameters
        ----------
        capacity : int
            Maximum number of items to store.
        save_first : bool
            If True, keep the first N items and ignore the rest.
            If False, keep the last N items using a fixed-size deque.
        """
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        # Still needed? Does original break with buffer?
        self.save_first = save_first

        if save_first:
            # For "first N" mode:
            # Use a normal list and stop accepting new items once full.
            self._data = []
            self._full = False
        else:
            # For "last N" mode:
            # Use deque(maxlen=N) so old items are automatically dropped.
            self._data = deque(maxlen=capacity)

    def add(self, item):
        """
        Add a new item to the buffer.

        Behavior:
        - save_first=True:
            Append until full, then ignore all further items.
        - save_first=False:
            Append always; deque automatically removes oldest items.
        """
        if self.save_first:
            if not self._full:
                self._data.append(item)
                # Mark as full once we reach capacity
                self._full = len(self._data) >= self.capacity
            # If full, silently ignore new items
        else:
            # Deque automatically maintains only the last N items
            self._data.append(item)

    def get(self):
        """
        Return the stored items as a list.

        Always returns a list regardless of internal storage type.
        """
        return list(self._data)

    def clear(self):
        """Clear all stored items."""
        if self.save_first:
            self._data.clear()
            self._full = False
        else:
            self._data.clear()

    def __len__(self):
        """Return the number of items currently stored."""
        return len(self._data)

    def __repr__(self):
        """
        Developer-friendly representation showing configuration and contents.
        """
        return f"Buffer(capacity={self.capacity}, save_first={self.save_first}, data={self.get()})"
