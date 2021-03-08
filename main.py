import importlib
import asyncio


import handler


async def new_server(host, port, handler):
    await asyncio.start_server(
        client_connected_cb=handler,
        host=host,
        port=port,
    )


async def new_client(host, port, handler):
    reader, writer = await asyncio.open_connection(
        host=host,
        port=port,
    )
    await asyncio.create_task(handler(reader, writer))


async def tcp_proxy(host, port):
    server_queue = asyncio.Queue()
    client_queue = asyncio.Queue()

    async def from_server(reader, writer):
        print('server connected')
        read_task = None
        write_task = None
        async def read():
            while True:
                data = await reader.read(4096)
                if len(data) < 1:
                    print('server disconnected')
                    write_task.cancel()
                    break
                importlib.reload(handler)
                data = await handler.msg_from_server(data)
                await client_queue.put(data)

        async def write():
            while True:
                data = await server_queue.get()
                importlib.reload(handler)
                data = await handler.msg_to_server(data)
                writer.write(data)
                await writer.drain()
        write_task = asyncio.create_task(write(), name='server.write')
        read_task = asyncio.create_task(read(), name='server.read')

    async def from_client(reader, writer):
        print('client connected')
        read_task = None
        write_task = None
        async def read():
            while True:
                data = await reader.read(4096)
                if len(data) < 1:
                    print('client disconnected')
                    write_task.cancel()
                    break
                importlib.reload(handler)
                data = await handler.msg_from_client(data)
                await server_queue.put(data)

        async def write():
            while True:
                data = await client_queue.get()
                importlib.reload(handler)
                data = await handler.msg_to_client(data)
                writer.write(data)
                await writer.drain()
        write_task = asyncio.create_task(write(), name='client.write')
        read_task = asyncio.create_task(read(), name='client.read')

    async def repl(reader, writer):
        print('repl connected')
        writer.write(b'connected to repl\n')
        await writer.drain()
        while True:
            data = await reader.read(4096)
            if len(data) < 1:
                print('repl disconnected')
                break
            importlib.reload(handler)
            await handler.msg_from_repl(data, writer, server_queue, client_queue)
    
    asyncio.create_task(new_server('0.0.0.0', 8080, repl), name='repl'),
    asyncio.create_task(new_server('0.0.0.0', port, from_client), name='client'),
    asyncio.create_task(new_client(host, port, from_server), name='server'),


async def main():
    asyncio.create_task(tcp_proxy('192.168.1.135', 2106), name='tcp_proxy'),
    await asyncio.gather(*asyncio.all_tasks())


if __name__ == '__main__':
    asyncio.run(main())
