#!/usr/bin/env python3

descr = """
This script will make the BinDB tables counts-consistent, i.e. such that the
count of each ngram is greater or equal to both:

- total count of all (n+1)grams whose first n tokens are equal to the ngram
- total count of all (n+1)grams whose last n tokens are equal to the ngram

Counts consistency is ensured by increasing lower-order counts based on higher-
order counts.
"""

import argparse
import collections
import itertools
import numpy
import os
import shutil

from pysteg.common.log import print_status
from pysteg.common.itertools import integrate_counts, maximise_counts
from pysteg.googlebooks import bindb

def drop_last_token(bindb_line):
    """Return the BinDB line with the last token removed."""
    return bindb.BinDBLine(bindb_line.ngram[:-1], bindb_line.count)

def right_integrate_counts(path, n):
    """
    Given the path to a BinDB file of order n, generate an iterator over
    sorted ((n-1)gram, count) tuples created by integrating out the first token.
    """

    print_status("Dumping", path, "to memory")

    ngrams_number = os.path.getsize(path) / bindb.line_size(n)

    # Format specifier for the numpy matrix used for sorting the mgrams
    dtp = (
        # (n-1) * little-endian 4 byte integers with token indices
        [("w{}".format(i),"<i4") for i in range(n-1)] +
        # little-endian 8 byte integer with the count
        [("count","<i8")]
    )

    # Progress bar code
    stages = tuple(range(1,26))
    milestones = collections.deque(map(
        lambda s: (round(s / stages[-1] * ngrams_number), s), stages
    ))

    # Dump all right mgrams to a numpy array
    mgrams = numpy.zeros(ngrams_number, dtype=dtp)
    i = 0

    with open(path, "rb") as f:
        for l in bindb.iter_bindb_file(f, n):
            mgrams[i] = l.ngram[1:] + (l.count,)
            i += 1

            if i == milestones[0][0]:
                done = round(100 / milestones[-1][1] * milestones.popleft()[1])
                print_status("{done}%".format(**locals()))

    # Sort the numpy array
    print_status("Sorting right integrated {n}grams".format(**locals()))
    mgrams.sort(order=["w{}".format(i) for i in range(n-1)])
    print_status("Sorted right integrated {n}grams".format(**locals()))

    def numpy_row2bindb_line(numpy_row):
        """
        Convert row of a numpy matrix with ngrams and counts to a BinDB line.
        """
        return bindb.BinDBLine(tuple(numpy_row)[:-1], numpy_row["count"])

    return integrate_counts(map(numpy_row2bindb_line, mgrams), bindb.BinDBLine)

def process_file(n):
    """Create a counts consistent BinDB table of order n."""
    ngrams_filename = "{n}gram".format(**locals())
    ngrams_input_path = os.path.join(args.input, ngrams_filename)
    ngrams_output_path = os.path.join(args.output, ngrams_filename)

    # The highest order table is consistent by definition
    if n == args.n_max:
        print_status("Copying", ngrams_input_path, "to", ngrams_output_path)
        shutil.copyfile(ngrams_input_path, ngrams_output_path)
    else:
        print_status("Creating counts-consistent {n}gram BinDB file".format(
            **locals()))

        # We need to use the already consistent table, hence reading ograms from
        # theoutput directory
        ograms_filename = "{}gram".format(n+1)
        ograms_path = os.path.join(args.output, ograms_filename)

        with open(ograms_path, "rb") as ograms_f, \
             open(ngrams_input_path, "rb") as ngrams_input_f, \
             open(ngrams_output_path, "wb") as ngrams_output_f:

            ograms = bindb.iter_bindb_file(ograms_f, n+1)

            # Make iterators over left and right integrated ograms
            left_integrated_ograms = integrate_counts(
                map(drop_last_token, ograms), bindb.BinDBLine
            )
            right_integrated_ograms = right_integrate_counts(ograms_path, n+1)

            # Maximise counts of left and right integrated ograms
            integrated_ograms = maximise_counts(
                left_integrated_ograms, right_integrated_ograms, bindb.BinDBLine
            )

            # Maximise counts of ngrams and integrated ograms
            ngrams = bindb.iter_bindb_file(ngrams_input_f, n)
            maximised_ngrams = maximise_counts(integrated_ograms, ngrams,
                                               bindb.BinDBLine)

            for l in maximised_ngrams:
                ngrams_output_f.write(bindb.pack_line(l, n))

    print_status("Saved counts-consistent {n}gram BinDB file "
                 "to".format(**locals()), ngrams_output_path)

# Define and parse arguments
parser = argparse.ArgumentParser(
    description=descr,
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("n_max", metavar="n", type=int, help="order of the model")
parser.add_argument("input", help="input directory of inconsistent BinDB files")
parser.add_argument("output",
    help="output directory of counts-consistent BinDB files")
args = parser.parse_args()

# Process the files
for n in range(args.n_max,0,-1):
    process_file(n)
