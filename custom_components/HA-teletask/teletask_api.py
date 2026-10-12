import asyncio
import logging

from .teletask_const import *

_LOGGER = logging.getLogger(__name__)

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

        self._ack_waiter = None
        self._reader_task = None
        self._keepalive_task = None
        self._send_lock = asyncio.Lock()

    def _get_function(self, tt_type):
        return TT_FUNCTIONS[tt_type.lower()]

    def _log_packet(self, direction, packet):
        _LOGGER.warning(
            "%s %s",
            direction,
            " ".join(f"{b:02X}" for b in packet),
        )

    def _checksum(self, data):
        return sum(data) & 0xFF

    def _verify_checksum(self, msg):
        return self._checksum(msg[:-1]) == msg[-1]

    async def connect(self):

        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port,
        )

        self._reader_task = asyncio.create_task(
            self._read_loop()
        )

        self._keepalive_task = asyncio.create_task(
            self._keepalive_loop()
        )

        _LOGGER.warning(
            "TT_CONNECTED %s:%s",
            self.host,
            self.port,
        )

    async def disconnect(self):

        if self._keepalive_task:
            self._keepalive_task.cancel()

        if self._reader_task:
            self._reader_task.cancel()

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        _LOGGER.warning("TT_DISCONNECTED")

    async def _keepalive_loop(self):

        while True:
            await asyncio.sleep(15)

            if self._ack_waiter is None:
                packet = self._build_packet(
                    COMMAND_KEEP_ALIVE,
                    [],
                )
                await self._send(packet)

    async def _read_loop(self):

        buffer = bytearray()

        while True:

            data = await self.reader.read(100)

            if not data:
                _LOGGER.warning("TT_SOCKET_CLOSED")
                return

            buffer.extend(data)

            cur = 0

            while cur < len(buffer):

                if buffer[cur] == COMMAND_ACK:

                    if self._ack_waiter:
                        self._ack_waiter.set()
                        self._ack_waiter = None

                    cur += 1
                    continue

                if buffer[cur] != STX:
                    cur += 1
                    continue

                if cur + 1 >= len(buffer):
                    break

                length = buffer[cur + 1]
                packet_length = length + 1

                if len(buffer) - cur < packet_length:
                    break

                packet = bytes(
                    buffer[cur:cur + packet_length]
                )

                if self._verify_checksum(packet):

                    self._log_packet(
                        "TT_RECV",
                        packet,
                    )

                    await self._process_packet(packet)

                cur += packet_length

            if cur:
                del buffer[:cur]

    async def _process_packet(self, packet):

        command = packet[2]

        if command == COMMAND_REPORT:

            cu = packet[3]
            fnc = packet[4]
            nr = (packet[5] << 8) + packet[6]

            _LOGGER.warning(
                "TT_REPORT cu=%s fnc=%s id=%s",
                cu,
                fnc,
                nr,
            )

            if self.writer:
                self.writer.write(
                    bytes([COMMAND_ACK])
                )
                await self.writer.drain()

    async def _send(self, packet):

        async with self._send_lock:

            self._ack_waiter = asyncio.Event()

            self._log_packet(
                "TT_SEND",
                packet,
            )

            self.writer.write(packet)
            await self.writer.drain()

            try:
                await asyncio.wait_for(
                    self._ack_waiter.wait(),
                    timeout=1.0,
                )

                _LOGGER.warning(
                    "TT_ACK_OK"
                )

            except asyncio.TimeoutError:

                _LOGGER.warning(
                    "TT_ACK_TIMEOUT"
                )

            finally:
                self._ack_waiter = None

    def _build_packet(
        self,
        command,
        parameters,
    ):

        packet = bytearray()

        packet.append(STX)

        length = 3 + len(parameters)

        packet.append(length)

        packet.append(command)

        packet.extend(parameters)

        packet.append(
            self._checksum(packet)
        )

        return bytes(packet)

    async def set_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
        value,
    ):

        function = self._get_function(
            tt_type
        )

        setting = (
            int(value)
            if tt_type == "dimmer"
            else SET_ON if value else SET_OFF
        )

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

        return True

    async def get_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
    ):

        function = self._get_function(
            tt_type
        )

        packet = self._build_packet(
            COMMAND_GET,
            [
                tt_cu,
                function,
                tt_id >> 8,
                tt_id & 0xFF,
            ],
        )

        await self._send(packet)

        return None