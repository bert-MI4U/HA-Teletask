import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

from .teletask_const import *

TT_FUNCTIONS = {
    "relay": FNC_RELAY,
    "dimmer": FNC_DIMMER,
    "locmood": FNC_LOCMOOD,
    "genmood": FNC_GENMOOD,
    "flag": FNC_FLAG,
}



class TeletaskApi:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None

        self._ack_waiter = None
        self._reader_task = None
        
    def _log_packet(self, direction, packet):

        _LOGGER.warning(
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
            self.port,
        )

        self._reader_task = asyncio.create_task(
            self._read_loop()
        )

        _LOGGER.warning("TT_CONNECTED")

    await self._send(
        self._build_packet(
            COMMAND_LOG,
            [
                FNC_RELAY,
                SET_ON,
            ],
        )
    )

    async def _read_loop(self):
        while True:
            data = await self.reader.read(100)

            if not data:
                _LOGGER.warning("TT_SOCKET_CLOSED")
                return

            for byte in data:

                if byte == 0x0A:
                    if self._ack_waiter:
                        self._ack_waiter.set()
                    continue

                # TODO:
                # accumulate packet bytes
                # parse Event Report (0x10)
                # dispatch callbacks


    async def _send(self, packet):

        self._ack_waiter = asyncio.Event()

        self.writer.write(packet)
        await self.writer.drain()

        try:
            await asyncio.wait_for(
                self._ack_waiter.wait(),
                timeout=1.0,
            )

            _LOGGER.warning("TT_ACK_OK")

        except asyncio.TimeoutError:
            _LOGGER.warning("TT_ACK_TIMEOUT")

        finally:
            self._ack_waiter = None

    async def set_state(...):

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

        await self._send(packet)



    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            
        _LOGGER.warning("TT_Disconnected")

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
            COMMAND_SET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
                setting,
            ],
        )

        _LOGGER.warning(
            "TT_SET type=%s cu=%s id=%s value=%s",
            tt_type,
            tt_cu,
            tt_id,
            value,
        )
        self._log_packet("TT_SEND", packet)
        self.writer.write(packet)
        await self.writer.drain()
        ack = await self.reader.read(1)
        _LOGGER.warning("TT_ACK %s", ack)

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

        _LOGGER.warning(
            "TT_SET type=%s cu=%s id=%s value=%s",
            tt_type,
            tt_cu,
            tt_id,
        )
        self._log_packet("TT_SEND", packet)
        self.writer.write(packet)
        await self.writer.drain()
        ack = await self.reader.read(1)
        _LOGGER.debug("TT_ACK %s", ack)
        if ack != b"\x0A":
            return None

        return None