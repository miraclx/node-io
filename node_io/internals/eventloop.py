import asyncio
import threading
from internals.debug import debug, debugwrapper
from node_events import EventEmitter


class EventQueue(asyncio.Queue):
    __forceIterStop = __ended = False
    @debugwrapper
    def __init__(self):
        super(EventQueue, self).__init__()

    @debugwrapper
    def push(self, block):
        self.put_nowait(block)

    async def __stripCoros(self):
        debug('async __stripCoros init')
        while not self.empty() and not self.ended:
            yield await self.get()
        self.__ended = True
        debug('async __stripCoros exit')

    async def _startIterator(self):
        debug('async __startIterator init')
        async for [coro, args] in self.__stripCoros():
            await coro if asyncio.iscoroutine(coro) else await coro(*args) if asyncio.iscoroutinefunction(coro) else coro(*args)
            self.task_done()
        debug('async __startIterator exit')

    @debugwrapper
    def forceStop(self):
        if self.__ended:
            raise RuntimeError("Queue iterator already ended")
        if self.__forceIterStop:
            raise RuntimeError("Queue iterator already force-stopped")
        self.__forceIterStop = self.__ended = True

    @property
    def ended(self):
        return self.__ended or self.__forceIterStop


class EventLoop(EventEmitter):
    _queue = _thread = __iteratorCoroutine = __autostarted = None

    @debugwrapper
    def __init__(self, name=None, *, autostart=True):
        self.name = name or 'asynceventloop'
        self._queue = EventQueue()
        self._thread = threading.Thread(
            target=lambda: asyncio.run(self.__asyncroot()))
        self._thread._loop = self
        self._thread.setName(self.name)
        self.__autostart = autostart
        super(EventLoop, self).__init__()

    async def __asyncroot(self):
        debug('async __asyncroot init')
        await self._queue._startIterator()
        self.emit('exit')
        debug('async __asyncroot exit')

    @debugwrapper
    def nextTick(self, coro, *args):
        self._queue.put_nowait([coro, args])
        if self.__autostart and not self.started:
            self.start()
            self.__autostarted = True

    @debugwrapper
    def start(self):
        if self.__autostarted:
            raise RuntimeError("thread has been autostarted previously. assign %s on the EventLoop constructor to disable this"
                               % 'autostart=False')
        self._thread.start()

    @property
    def started(self):
        return self._thread._started.is_set()


def getRunningThread():
    return threading.current_thread()


def getRunningLoop():
    loop = getattr(getRunningThread(), '_loop', None)
    if loop:
        return loop
    else:
        raise RuntimeError('no running event loop')


get_running_thread = getRunningThread
get_running_loop = getRunningLoop
