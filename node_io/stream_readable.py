from node_buffer import Buffer
from node_io.stream_base import Stream
from internals.bufferlist import BufferList
from internals.debug import debug, debugwrapper


class ReadableState:
    def __init__(self, *, highWaterMark=None):
        self.buffer = BufferList()
        self.highWaterMark = highWaterMark or 16 * 2 ** 10  # 16KB
        self.flowing = self.reading = self.ended = self.maybeReadingMore = False
        self.paused = True
        self.length = 0
        # self.destroyed = False


class Readable(Stream):
    def __init__(self, *, read=None, highWaterMark=None):
        super(Readable, self).__init__()

        self._read = read or self.getUnimpl(
            'The _read() method is not implemented')
        self._readableState = ReadableState(highWaterMark=highWaterMark)
        self.readableBuffer = self._readableState.buffer

        def handleAddData():
            debug("on 'addlistener:data'", 'Set stream to flow mode')
            self.resume()
            debug("on 'addlistener:data'", 'Done setting stream to flow')

        def handleRmData():
            debug("on 'rmlistener:data'")
            if not self.hasListeners('data'):
                debug("on 'rmlistener:data'", 'Pause stream')
                self.pause()
                debug("on 'rmlistener:data'", 'Done pausing stream')

        self.on('addlistener:data', handleAddData)
        self.on('rmlistener:data', handleRmData)

    @debugwrapper
    def push(self, data):
        # debug("push()", f'{len(data)} bytes')
        self.__addChunk(data, False)

    @debugwrapper
    def unshift(self, data):
        # debug("unshift()", f'{len(data)} bytes')
        self.__addChunk(data, True)

    @debugwrapper(end=2)
    def __addChunk(self, chunk, addToFront=False):
        state = self._readableState
        if chunk == None:
            state.reading = False
            self.__onEofChunk()
        else:
            chunk = Buffer.new(chunk)
            state.reading = False
            if state.flowing and state.buffer.length == 0:
                debug("__addChunk emit 'data'",
                      'Reason: Flowing with empty queue')
                self.emit('data', chunk)
            elif len(chunk) > 0:
                debug(
                    "__addChunk buffer",
                    f'Reason: {"Stream not flowing" if not state.flowing else "Bufferlist not empty"}'
                )
                state.length += len(chunk)
                self._readableState.buffer.unshift(
                    chunk) if addToFront else self._readableState.buffer.push(chunk)
                self.__maybeReadMore()
            else:
                self.__maybeReadMore()
        return not state.ended and state.length < state.highWaterMark or state.length == 0

    @debugwrapper
    def __onEofChunk(self):
        state = self._readableState
        if (state.ended):
            return
        debug("__onEofChunk", 'state.ended = True')
        state.ended = True

    @debugwrapper
    def __maybeReadMore(self):
        state = self._readableState
        debug("__maybeReadMore", 'state.readingMore = True')
        state.readingMore = True

        def shouldRead():
            return state.flowing and not state.reading and not state.ended and \
                (state.length < state.highWaterMark or state.length == 0)

        if (not shouldRead()):
            debug("__maybeReadMore", "skip iterloop, doesn't meet loop condition")

        while (
            # not state.reading and not state.ended and
            # (state.length < state.highWaterMark or
            #  (state.flowing and state.length == 0)
            #  )
            shouldRead()
        ):
            debug("__maybeReadMore iterloop", 'reading...')
            debug("__maybeReadMore read()")
            if (len(self.read() or '') == 0):
                debug("__maybeReadMore iterloop", 'breaking')
                break
        debug("__maybeReadMore", 'state.readingMore = False')
        state.readingMore = False

    @debugwrapper
    def read(self, n=None):
        state = self._readableState
        ret = None
        if state.ended or state.reading:
            debug('read', 'reading or ended')
        else:
            debug('read', 'has \'data\' event listeners, reading')
            debug('read', 'state.reading = True')
            state.reading = True
            debug('read _read()')
            self._read(state.highWaterMark)
            n = self.__howMuchToRead(n)
            debug('read', f'Pulling {n} bytes from buffer')
            ret = state.buffer.consume(n)
            state.length -= len(ret or '')
        if ret:
            debug("read emit 'data'")
            self.emit('data', ret)
        return ret

    def __howMuchToRead(self, n=None):
        state = self._readableState
        from internals.hwm import computeNewHighWaterMark
        if n == None:
            debug("__howMuchToRead",
                  f'n is None, set n to highWaterMark [{state.highWaterMark}]')
            n = state.highWaterMark
        if not isinstance(n, (float, int)):
            ret = state.buffer.head.data.length if state.length else state.length
            debug("__howMuchToRead",
                  'n is neither int nor float, return buffer length [{ret}]')
            return ret
        if n > state.highWaterMark:
            debug("__howMuchToRead", 'n > state.highWaterMark, update highWaterMark')
            state.highWaterMark = computeNewHighWaterMark(n)
        if n <= state.length:
            debug("__howMuchToRead", f'n <= state.length, return n [{n}]')
            return n
        debug("__howMuchToRead", f'return buffer length [{state.length}]')
        return state.length

    @debugwrapper
    def __resume(self):
        state = self._readableState
        if (state.flowing):
            debug('__resume', 'stream already flowing')
        else:
            debug('__resume', 'state.flowing = True')
            state.flowing = True
            if (not state.reading):
                self.read()
            debug("__resume emit 'resume'")
            self.emit('resume')
            self.__flow()
            if (state.flowing and not state.reading):
                self.read()
        debug('__resume', 'state.paused = False')
        state.paused = False

    @debugwrapper
    def __pause(self):
        state = self._readableState
        if (state.flowing):
            debug('__pause', 'state.flowing = False')
            state.flowing = False
            debug("__pause emit 'pause'")
            self.emit("pause")
        else:
            debug('__pause', 'Stream already static, not flowing')
        debug('__pause', 'state.paused = True')
        state.paused = True

    @debugwrapper
    def __flow(self):
        state = self._readableState
        debug('__flow', 'Flow mode enabled')
        while (state.flowing and self.read()):
            pass
        debug('__flow', 'Detached from flow mode')

    @debugwrapper
    def resume(self):
        self.__resume()

    @debugwrapper
    def pause(self):
        self.__pause()

    @property
    def readable(self):
        state = self._readableState
        return state.flowing and not state.reading and not state.ended


'<Readable object=/file.txt size=Infinite highWaterMark=16355 paused=False ended=False closed=False reading=True>'
"""
Readable {
    size: 2888487294,
    ended: False,
    closed: False,
    object: 'file.txt',
    paused: False,
    reading: False,
    flowing: False,
    destroyed: False,
    objectMode: False,
    highWaterMark: 65535
}
"""
