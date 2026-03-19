#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import types
from typing import Callable


class AsyncSignal():
    def __init__(self, *param_types):
        if not all(isinstance(t, (type, types.GenericAlias)) for t in param_types):
            raise AssertionError('Only "Type" class is allowed')

        self._types = param_types
        self._callbacks: set[Callable] = set()
        self._pending_tasks: set[asyncio.Task] = set()

    def asyncConnect(self, func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise AssertionError('Not corouting function')

        if func in self._callbacks:
            raise AssertionError('Already connected')

        self._callbacks.add(func)

    def disconnect(self, func: Callable):
        if func not in self._callbacks:
            raise AssertionError('Not connected')

        self._callbacks.remove(func)

    async def emit(self, *args, **kwargs):
        if len(args) != len(self._types):
            raise AssertionError('Wrong number of Parameters')

        for arg, type_ in zip(args, self._types):
            if not isinstance(arg, type_):
                raise AssertionError('Wrong parameter type')

        for cb in self._callbacks:
            await cb(*args, **kwargs)

    def emitLater(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        for cb in self._callbacks:
            task = loop.create_task(cb(*args, **kwargs))
            self._pending_tasks.add(task)
            task.add_done_callback(self._pending_tasks.discard)


async def main():
    signal = AsyncSignal(str, int)
    await signal.emit('test', 1)

    signal = AsyncSignal(str)
    await signal.emit('test')

    signal = AsyncSignal()
    await signal.emit()


if __name__ == '__main__':
    asyncio.run(main())
