import asyncio


def format_hex(data):
    return data.hex().upper()

def format_ascii(data):
    return ''.join(map(lambda x: chr(x) if (False
        or ord('a') <= x <= ord('z')
        or ord('A') <= x <= ord('Z')
        or ord('0') <= x <= ord('9')
    ) else '.', data))


async def msg_from_server(data):
    print(f'{"from": <5} server {len(data): 4} {format_hex(data)} {format_ascii(data)}')
    return data

async def msg_to_server(data):
    # print(f'{"to": <5} server {len(data): 4} {format_hex(data)} {format_ascii(data)}')
    return data

async def msg_from_client(data):
    print(f'{"from": <5} client {len(data): 4} {format_hex(data)} {format_ascii(data)}')
    return data

async def msg_to_client(data):
    # print(f'{"to": <5} client {len(data): 4} {format_hex(data)} {format_ascii(data)}')
    return data

async def msg_from_repl(data, writer, server_queue, client_queue):
    print(f'{"from": <5} repl {len(data): 4} {data}')
    if data.startswith(b'list tasks'):
        all_tasks = list(map(lambda task: task.get_name(), asyncio.all_tasks()))
        writer.write(str(all_tasks).encode('ascii'))
        await writer.drain()
    return data
