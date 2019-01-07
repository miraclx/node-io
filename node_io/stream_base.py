import io
from node_events import EventEmitter


class StreamBase(io.BytesIO):
    pass


class Stream(EventEmitter):
    # def __init__(self):
        # self.__underlayer = StreamBase

    def getUnimpl(self, msg):
        def _undef(self, *args):
            raise NotImplementedError(msg)
        return _undef
