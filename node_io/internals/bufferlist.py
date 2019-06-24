from rshift import rshift
from node_buffer import Buffer


class Entry:
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next

    def __repr__(self): return \
        ('\x1b[32mEntry\x1b[0m {ob}{nl}\x1b[36mdata\x1b[0m: %a,{nl}\x1b[36mnext\x1b[0m:%s %s {cb}'
         .format(nl='\n  ' if self.next else ' ', ob='{', cb='}') % (
             self.data, '\n   ' if self.next else '', ('%s' % self.next).replace('\n', '\n    ' if self.next else '\n  ')))

    def __str__(self): return self.__repr__()


class BufferList:
    def __init__(self):
        self.head = self.tail = Entry()
        self.length = 0

    def __repr__(self):
        return 'BufferList {ob}{nl}head: {0},{nl}tail: {1},{nl}length: \x1b[33m{2}\x1b[0m {cb}'\
            .format(*(['\x1b[34m[object]\x1b[0m']*2 if self.head.next or self.tail.next else (self.head, self.tail)), self.length, ob='{', cb='}', nl=' ' if self.head.next else '\n  ')

    def push(self, v):
        entry = Entry(data=Buffer.new(v))
        if (self.length > 0):
            self.tail.next = entry
        else:
            self.head = entry
        self.tail = entry
        self.length += 1

    def unshift(self, v):
        entry = Entry(data=Buffer.new(v), next=self.head)
        if (self.length > 0):
            self.tail = entry
        self.head = entry
        self.length += 1

    def shift(self):
        if (self.length == 0):
            return
        ret = self.head.data
        if (self.length == 1):
            self.head = self.tail = Entry()
        else:
            self.head = self.head.next
        self.length -= 1
        return ret

    def clear(self):
        self.head = self.tail = Entry()
        self.length = 0

    def join(self, s):
        if (self.length == 0):
            return ''
        p = self.head
        ret = p.data.decode()
        # while (p=p.next):
        while (p.next):
            ret += s + p.data
        return ret

    def concat(self, n):
        if (self.length == 0):
            return Buffer()
        ret = Buffer.alloc(rshift(n, 0))
        p = self.head
        i = 0
        while p:
            Buffer.copy(p.data, ret, i)
            i += len(p.data)
            p = p.next
        return ret

    def consume(self, n, hasStrings=False):
        ret = None
        if (n < len(self.head.data)):
            ret = self.head.data.slice(0, n)
            self.head.data = self.head.data.slice(n)
        elif (n == len(self.head.data)):
            ret = self.shift()
        else:
            ret = self._getBuffer(n)
        return ret

    def first(self):
        return self.head.data

    def _getBuffer(self, n):
        ret = Buffer.alloc(n)
        p = self.head
        c = 1
        # print(p)
        p.data.copy(ret)
        n -= len(p.data)
        while (p.next):
            p = p.next
            buf = p.data
            nb = buf.length if n > buf.length else n
            buf.copy(ret, ret.length - n, 0, nb)
            n -= nb
            if (n == 0):
                if (nb == buf.length):
                    c += 1
                    if (p.next):
                        self.head = p.next
                    else:
                        self.head = self.tail = Entry()
                else:
                    self.head = p
                    p.data = buf.slice(nb)
                break
            c += 1
        self.length -= c
        return ret
