
# List with a fixed number of elements. As you add more, the ones at the back fall off
# get_past_item lets you retrieve the nth most recent entry (0 is the latest one)
# use this for storing a history of things
class CircularList(object):
    def __init__(self, size):
        """Initialization"""
        self.index = size-1;
        self.size = size
        self._data = [None] * size

    def log_state(self, title):
        print("\nlog state: {}".format(title))
        for i, image in enumerate(self._data):
            print("{}: {} - {}".format(i, "Full" if (image is not None) else "Empty", "Current" if self.index == i else ""))

    def append(self, value):
        """Append an element"""
        self.index = (self.index + 1) % self.size
        self._data[self.index] = value
        #self.log_state("append")

    def roll_back(self, count_back):
        assert self.is_valid_count_back(count_back)
        assert self.has_past_item(count_back)

        i = 0
        while i < count_back:
            use_index = self.calc_count_back_index(i)
            self._data[use_index] = None
            i += 1

        self.index = self.calc_count_back_index(count_back)
        #self.log_state("roll_back")

    def is_valid_count_back(self, count_back):
        return count_back < self.size

    """Get element by index, relative to the current index"""
    def get_past_item(self, count_back):
        assert self.has_past_item(count_back)

        use_index = self.calc_count_back_index(count_back)
        return self._data[use_index]
    
    def has_past_item(self, count_back):
        if not self.is_valid_count_back(count_back):
            return False

        use_index = self.calc_count_back_index(count_back)
        return self._data[use_index] is not None

    def calc_count_back_index(self, count_back):
        return (self.index + self.size - count_back) % self.size

    def __repr__(self):
        """Return string representation"""
        return self._data.__repr__() + ' (' + str(len(self._data))+' items)'
