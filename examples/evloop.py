import asyncio
from internals.eventloop import EventLoop, printprocess, get_running_loop


def nestedfn():
    printprocess("hello from nestedfn")


async def asyncfunction1():
    process = get_running_loop()
    printprocess("asyncfunction1 init")
    await asyncio.sleep(2)
    process.nextTick(nestedfn)
    printprocess("asyncfunction1 exit")


async def asyncfunction2():
    process = get_running_loop()
    printprocess("asyncfunction2 init")
    await asyncio.sleep(2)
    process.nextTick(nestedfn)
    printprocess("asyncfunction2 exit")


def collate():
    printprocess('collate init')
    process = get_running_loop()
    process.nextTick(asyncio.wait([asyncfunction1(), asyncfunction2()]))
    printprocess('collate exit')


printprocess("start")
i = 0
while i < 2:
    process = EventLoop(f'Thread - {i}')
    process.on('exit', lambda: printprocess("quit"))
    process.nextTick(collate)
    i += 1
printprocess("end")
