import collections

import sympy

from pysteg.coding.interval import create_interval
from pysteg.coding.interval import find_superinterval
from pysteg.coding.interval import is_subinterval
from pysteg.coding.interval import random_interval
from pysteg.coding.interval import select_subinterval

# Result of looking for the next symbol given context and current search
# interval. The elements of the output tuple are:
#
# symbol  - symbol whose conditional interval is a superinterval of the search
#           interval
# ssi     - search interval as a ratio of the conditional interval of the symbol
#           (scaled search interval)
NextSymbolSearchResult = collections.namedtuple("NextSymbolSearchResult",
    "symbol ssi")

DecodedSequence = collections.namedtuple("DecodedSequence", "sequence interval")

def decode(next, interval, verbose=False):
    """
    Decode an interval using the supplied "next token" function. Decoding ends
    when interval corresponding to the output sequence is the smallest
    superinterval of the input interval.
    """

    sequence = []
    search_result = next(interval, tuple(sequence))

    while search_result is not None:
        if verbose: print(search_result.symbol)
        sequence.append(search_result.symbol)
        output_interval = find_superinterval(interval, search_result.ssi)
        search_result = next(search_result.ssi, tuple(sequence))

    return DecodedSequence(tuple(sequence), output_interval)

def deep_decode(next, i, end=None, seed=None, verbose=False):
    """
    Decode an interval using a randomly chosen refinement of the input interval
    and the supplied "next token" function. The input interval is refined until
    the interval corresponding to the output sequence is its subinterval. The
    output sequence is optionally continued until a specified end symbol is
    generated.
    """

    # i   - actual input interval
    # ir  - refined input interval
    # r   - refinement of the actual input interval
    # o   - output sequence interval
    # irs - refined input interval scaled as a part of the output interval

    # Number of random bits of refinement
    n = 100

    # Initial refined input intervals
    ir = i
    irs = i

    output_sequence = []

    while True:
        # Refine the input interval by a chosen ratio
        r = random_interval(n, seed=seed)
        ir = select_subinterval(ir, r)
        irs = select_subinterval(irs, r)

        if verbose: print("Refined input interval by: " + str(r))

        # Search for the next symbol
        search_result = next(irs, tuple(output_sequence))

        while search_result is not None:
            # The search procedure gives us the next symbol and the refined
            # input interval scaled inside the current output interval
            (symbol, irs) = (search_result.symbol, search_result.ssi)
            output_sequence.append(symbol)

            # Calculate the current output interval using the refined input
            # interval scaled to it and the knowledge of actual refined input
            # interval
            o = find_superinterval(ir, irs)

            if verbose: print(symbol)

            # Terminate generating the output sequence if the output interval
            # becomes a subinterval of the actual input interval. Optionally
            # wait for generating the end symbol.
            if is_subinterval(o, i) and (end is None or symbol == end):
                return DecodedSequence(tuple(output_sequence), o)

            search_result = next(irs, tuple(output_sequence))

def encode(conditional_interval, sequence, verbose=False):
    """
    Encode a sequence into an exact interval using the supplied "conditional
    subinterval" function.
    """

    interval = create_interval(0,1)

    for i in range(len(sequence)):
        if verbose: print(sequence[i])
        interval = select_subinterval(
            interval, conditional_interval(sequence[i], sequence[:i])
        )

    return interval
