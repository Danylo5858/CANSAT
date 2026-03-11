import asyncio
from sx126x import SX126X, Address

def start():
    asyncio.run(main())

async def main():
    await recieve()

async def receive():
    lora = SX126X(Address(6, 9))
    address, data = await lora.rx()
    print(f"Recibido de {address}: {data.decode()}")
