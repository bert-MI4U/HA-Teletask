import asyncio
import logging

from .teletask_const import *

TT_FUNCTIONS = {
    "relay": FNC_RELAY,
    "dimmer": FNC_DIMMER,
    "locmood": FNC_LOCMOOD,
    "genmood": FNC_GENMOOD,
    "flag": FNC_FLAG,
}

_LOGGER = logging.getLogger(__name__)


class teletask_api:

    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None
    
    def _log_packet(self, direction, packet):

        _LOGGER.debug(
            "%s %s",
            direction,
            " ".join(f"{b:02X}" for b in packet),
        )

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

         _LOGGER.info(
            "Connected to Teletask %s:%s",
            self.host,
            self.port,
        )

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
        _LOGGER.info("Disconnected")

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
        
        _LOGGER = logging.getLogger(__name__)

        if tt_type == "dimmer":
            setting = int(value)
        else:
            setting = SET_ON if value else SET_OFF

        packet = self._build_packet(
            COMMAND_SET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
                setting,
            ],
        )

        self._log_packet("SEND", packet)
            
        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)
        print(f"ACK={ack}")

        return ack == b"\x0A"
        
    async def get_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
    ):

        function = self._get_function(tt_type)

        packet = self._build_packet(
            COMMAND_GET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
            ],
        )

        self._log_packet("RECV", packet)

        self.writer.write(packet)
        await self.writer.drain()

        ack = await self.reader.read(1)

        if ack != b"\x0A":
            return None

        return None