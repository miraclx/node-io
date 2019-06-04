# -*- coding: utf-8 -*-

"""
                    node_io:
A mini-rewrite of the NodeJS Stream API for asynchronous stream management
capabilities based on the async-like `node-events.py` script by Miraulous Owonubi
"""

__author__ = "Miraculous Owonubi"
__copyright__ = "Copyright 2019"
__credits__ = ["Miraculous Owonubi"]
__license__ = "Apache-2.0"
__version__ = "0.1.0"
__maintainer__ = "Miraculous Owonubi"
__email__ = "omiraculous@gmail.com"
__status__ = "Development"

import io


class StreamConstants:
    READABLE_STREAM = 0
    TRANSFORM_STREAM = 1
    WRITABLE_STREAM = 2
    READABLE_WATERMARK = 2 ** 16 - 1
    WRITABLE_WATERMARK = 2 ** 16 - 1


class StreamBase(io.RawIOBase):
    pass


def validate(root, self, msg="Failed to validate execution manner, instance method irrationally called"):
    root = root if type(root) is list else [root]
    if not type(self) in root:
        raise Exception(msg)


class Stream():
    def __init__(self, _type):
        self.type = _type
        self._core = StreamBase()

    @property
    def position(self):
        return self._core.tell()

    def destroy(self):
        self._core.close()

    @staticmethod
    def is_stream(object):
        return type(object) is Stream


class Readable(Stream):
    readable_buffer = bytearray()
    readable_water_mark = StreamConstants.READABLE_WATERMARK

    def __init__(self):
        super(Readable, self).__init__(StreamConstants.READABLE_STREAM)
        self.pipes = []

    @property
    def pipe_count(self):
        return len(self.pipes)

    @property
    def readable(self):
        return self._core.readable()

    def push(self, chunk):
        self._core.write(chunk)

    def read(self, length=readable_water_mark):
        validate(Readable, self)
        ret = bytearray()
        if self.readable:
            self.__read(length)
            ret = self.readable_buffer
        return ret

    def __read(self, length):  # Internal push method
        self.readable_buffer = self._core.read(length)

    def pipe(self, other, end=True):
        validate([Readable, Transform], self,
                 "Piping is restricted to `Readable`-like streams only")
        self.pipes.append(other)
        while other.writable and self.readable:
            with self.read() as content:
                other.write(content)

    def unpipe(self, other):
        validate(Readable, self,
                 "Unpiping is restricted to `Readable`-like streams only")
        if other in self.pipes:
            self.pipes.remove(other)
            other.end()
        raise Exception("Error removing pipe destination, unexistent")


class Writable(Stream):
    writable_buffer = bytearray()
    writable_water_mark = StreamConstants.WRITABLE_WATERMARK

    def __init__(self):
        super(Writable, self).__init__(StreamConstants.WRITABLE_STREAM)

    @property
    def writable(self):
        return self._core.writable()

    def write(self, chunk):
        validate(Writable, self)
        ret = 0
        if self.writable:
            self.writable_buffer = chunk
            ret = self.__write()
        return ret

    def end(self, chunk):
        self.write(chunk)
        self._core.close()

    def __write(self):  # Internal write method
        return self._core.write(self.writable_buffer)


class Transform(Readable, Writable):
    def __init__(self):
        Stream.__init__(self, StreamConstants.TRANSFORM_STREAM)
