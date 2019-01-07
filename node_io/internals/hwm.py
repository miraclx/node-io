MAX_HWM = 0x800000


def computeNewHighWaterMark(n):
    from internals.rshift import rshift
    if (n >= MAX_HWM):
        n = MAX_HWM
    else:
        # Get the next highest power of 2 to prevent increasing hwm excessively in
        # tiny amounts
        n -= 1
        n |= rshift(n,  1)
        n |= rshift(n,  2)
        n |= rshift(n,  4)
        n |= rshift(n,  8)
        n |= rshift(n, 16)
        n += 1
    return n
