#!/usr/bin/env python3

import sympy

from pysteg.coding.interval import create_interval
from pysteg.coding.rational_ac import decode
from pysteg.googlebooks import bindb

# Set language model parameters
n = 5
start = 322578
end = 322577
beta = 1
gamma = 0.1
offset = 0

print("n: {n}".format(**locals()))
print("start: {start}".format(**locals()))
print("end: {end}".format(**locals()))
print("beta: {beta}".format(**locals()))
print("gamma: {gamma}".format(**locals()))
print("offset: {offset}".format(**locals()))
print()

# Load language model
lm = bindb.BinDBLM("/Users/kkom/Desktop/bindb-normalised/counts-consistent-tables", n, start, end, beta, gamma, offset)

# Create an interval
interval = create_interval(
    sympy.Rational(3,7),
    sympy.Rational(1, sympy.Pow(10,200))
)

print("Decoding: " + str(interval))
print()

sequence = decode(lm.next, interval)
print()

# Load index
with open("/Users/kkom/Desktop/bindb-normalised/index", "r") as f:
    index = bindb.BinDBIndex(f)

print("Decoded to: " + " ".join(map(index.i2s, sequence)))
