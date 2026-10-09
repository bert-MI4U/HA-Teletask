import asyncio

from teletask_const import *

class teletask_api:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port
        )

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    def _build_packet(self, command, parameters):

        packet = bytearray()

        packet.append(STX)

        length = 3 + len(parameters)
        packet.append(length)

        packet.append(command)

        packet.extend(parameters)

        checksum = sum(packet) & 0xFF
        packet.append(checksum)

        return bytes(packet)

    async def set_relay_state(
        self,
        central_unit,
        relay_id,
        state
    ):

        setting = SET_ON if state else SET_OFF

        packet = self._build_packet(
            COMMAND_FUNCTION_SET,
            [
                central_unit,
                FUNCTION_RELAY,
                (relay_id >> 8) & 0xFF,
                relay_id & 0xFF,
                setting
            ]
        )

        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)

        return ack == b'\x0A'

    async def get_relay_state(
        self,
        central_unit,
        relay_id
    ):

        packet = self._build_packet(
            COMMAND_FUNCTION_GET,
            [
                central_unit,
                FUNCTION_RELAY,
                (relay_id >> 8) & 0xFF,
                relay_id & 0xFF
            ]
        )

        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)

        if ack != b'\x0A':
            return None

        return True