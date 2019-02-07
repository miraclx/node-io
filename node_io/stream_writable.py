from node_io.stream_base import Stream
from internals.bufferlist import BufferList


class WritableState:
    def __init__(self, *, highWaterMark=None):
        self.buffer = BufferList()
        self.highWaterMark = highWaterMark or 16 * 2 ** 10  # 16KB
        self.writing = self.ended = False
        self.length = 0
        # self.finished = False
        # self.destroyed = False


class Writable(Stream):
    def __init__(self, *, write=None, drain=None, highWaterMark=None):
        super(Writable, self).__init__()

        self._write = write or self.getUnimpl(
            'The _write() method is not implemented')
        self._drain = drain or self.getUnimpl(
            'The _drain() method is not implemented')
        self._writableState = WritableState(highWaterMark=highWaterMark)
        self.writableBuffer = self._writableState.buffer

    def write(self, data, callback=None):
        if data:
            self.writeOrBuffer(data, callback)

    def writeOrBuffer(self, data, callback):
        state = self._writableState
        state.buffer.push(data)
        if self.writable:
            state.writing = True
            self._write(state.buffer.consume(state.highWaterMark))
            self.emit('drain')
            state.writing = False
        if callable(callback):
            callback()

    @property
    def writable(self):
        state = self._writableState
        return not state.writing and not state.ended


'<Writable object=/file.txt closed=false>'
