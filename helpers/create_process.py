
import asyncio 

async def create_process(command):
    process = await asyncio.create_subprocess_exec(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    print(stdout.decode())
    if stderr:
        print(stderr.decode())

