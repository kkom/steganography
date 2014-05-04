import functools
import struct

class BinDBIndex:
    """
    Index of the bindb database. Provides fast methods to go between indices and
    tokens.
    """

    def __init__(self, f):
        """
        Initialise the index. The index is a text file that for each token has
        a single line containing 3 tab separated values:

        1. index of the token (from 1 to vocabulary size V)
        2. token
        3. partition of the token

        The index has to be already sorted by 1.
        """

        self.index_dict = {}
        index_list = []

        for l in f:
            l_split = l[:-1].split("\t")
            self.index_dict[l_split[1]] = (int(l_split[0]), l_split[2])
            index_list.append(l_split[1])

        self.index_tuple = tuple(index_list)

    def i2t(self, i):
        """Return the token gives its index."""
        return self.index_tuple[i-1]

    def t2i(self, t):
        """Return the index of a token."""
        return self.index_dict[t][0]

    def t2p(self, t):
        """Return the partition of a token."""
        return self.index_dict[t][1]

@functools.lru_cache(maxsize=8)
def fmt(n):
    """Format specifier for a line of the bindb file of particular order n."""
    return (
        "<" +     # little-endian byte order (native for x86 and x86-64 CPUs)
        n * "i" + # n * 4 byte integers with token indices
        "q"       # 8 byte integer with ngram count
    )

def read_line(f, n, l):
    """
    Return the l'th (1-indexed) line of a bindb file as an (ngram, count) tuple.
    """

    # 4 bytes for each word index and 8 bytes for the count
    line_size = 4*n+8

    # Go to the l'th line
    f.seek((l-1)*line_size)

    # Unpack the line
    line = struct.unpack(fmt(n), f.read(line_size))

    return (line[:-1], line[-1])
