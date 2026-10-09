import asyncio

from .teletask_const import *

TT_FUNCTIONS = {
    "relay": FNC_RELAY,
    "dimmer": FNC_DIMMER,
    "locmood": FNC_LOCMOOD,
    "genmood": FNC_GENMOOD,
    "flag": FNC_FLAG,
}

class teletask_api:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None
    
    def _get_function(self, tt_type):

        try:
            return TT_FUNCTIONS[tt_type.lower()]
        except KeyError:
            raise ValueError(
                f"Unsupported Teletask type: {tt_type}"
            )
        
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

    async def set_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
        value,
    ):

        function = self._get_function(tt_type)

        if tt_type == "dimmer":
            setting = int(value)
        else:
            setting = SET_ON if value else SET_OFF

        packet = self._build_packet(
            COMMAND_FUNCTION_SET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
                setting,
            ],
        )

        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)

        return ack == b"\x0A"
        
    async def get_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
    ):

        function = self._get_function(tt_type)

        packet = self._build_packet(
            COMMAND_FUNCTION_GET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
            ],
        )

        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)

        if ack != b"\x0A":
            return None

        return None