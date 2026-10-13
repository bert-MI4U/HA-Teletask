#Connect to Teletask controller through api.
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
    #create api object
        self.host = host
        self.port = port

        self.reader = None
        self.writer = None

        self._ack_waiter = None
        self._reader_task = None
        self._keepalive_task = None
        self._send_lock = asyncio.Lock()
        self._event_callback = None
        self._listeners = {}


    def _get_function(self, tt_type):
        return TT_FUNCTIONS[tt_type.lower()]

    def _log_packet(self, direction, packet):
        _LOGGER.info(
            "%s %s",
            direction,
            " ".join(f"{b:02X}" for b in packet),
        )

    def _checksum(self, data):
        return sum(data) & 0xFF

    def _verify_checksum(self, msg):
        return self._checksum(msg[:-1]) == msg[-1]

    def register_listener(
    #Create 1 listener for Teletask as it sends all information to all listeners if there are more.
        self,
        tt_cu,
        tt_type,
        tt_id,
        listener,
    ):
        key = (
            tt_cu,
            tt_type,
            tt_id,
        )

        self._listeners[key] = listener
    
    async def connect(self):
        #Connect to Teletask controller 
        self.reader, self.writer = await asyncio.open_connection(
            self.host,
            self.port,
        )
        #start read_loop
        self._reader_task = asyncio.create_task(
            self._read_loop()
        )

        def _reader_done(task):
            try:
                task.result()
            except Exception:
                _LOGGER.exception(
                    "TT_READER_TASK_CRASHED"
                )

        self._reader_task.add_done_callback(
            _reader_done
        )
        
        #start keepalive_loop
        self._keepalive_task = asyncio.create_task(
            self._keepalive_loop()
        )

        _LOGGER.info(
            "TT_CONNECTED %s:%s",
            self.host,
            self.port,
        )
        
        _LOGGER.debug(
            "TT_ENABLE_RELAY_LOG"
        )

        await self.function_log(
            FNC_RELAY,
            SET_ON,
        )

        _LOGGER.debug(
            "TT_ENABLE_DIMMER_LOG"
        )

        await self.function_log(
            FNC_DIMMER,
            SET_ON,
        )
        
    async def request_state(
        self,
        tt_type,
        tt_cu,
        tt_id,
    ):
    #request Teletask status after initial startup
    
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

        await self._send(packet) 

    async def function_log(
    #tell Teletask to send events for devices
        self,
        tt_type,
        tt_state,
    ):
        _LOGGER.debug(
            "TT_FUNCTION_LOG fnc=%s state=%s",
            tt_type,
            tt_state,
        )

        packet = self._build_packet(
            COMMAND_LOG,
            [
                tt_type,
                tt_state,
            ],
        )

        await self._send(packet)

    async def disconnect(self):

        if self._keepalive_task:
            self._keepalive_task.cancel()

        if self._reader_task:
            self._reader_task.cancel()

        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except ConnectionResetError:
                pass
        
        _LOGGER.warning("TT_DISCONNECTED")

    async def _keepalive_loop(self):
    #every 15seconds a keepalive is sent to Teletask to keep feedback going

        while True:
            await asyncio.sleep(15)

            if self._ack_waiter is None:
                packet = self._build_packet(
                    COMMAND_KEEP_ALIVE,
                    [],
                )
                await self._send(packet)

    async def _read_loop(self):
    #receive teletask information (bytes)    
        _LOGGER.debug("TT_READLOOP_STARTED")

        buffer = bytearray()

        while True:

            try:
                data = await self.reader.read(100)

                _LOGGER.debug(
                    "TT_READLOOP_RAW %r",
                    data,
                )

            except Exception as err:
                _LOGGER.exception(
                    "TT_READLOOP_EXCEPTION %s",
                    err,
                )
                raise
 
            buffer.extend(data)

            cur = 0

            while cur < len(buffer):
                #detect ACK
                if buffer[cur] == COMMAND_ACK:

                    if self._ack_waiter:
                        self._ack_waiter.set()
                        self._ack_waiter = None

                    cur += 1
                    continue
                #detect packet start
                if buffer[cur] != STX:
                    cur += 1
                    continue
                #extract packet
                if cur + 1 >= len(buffer):
                    break

                length = buffer[cur + 1]
                packet_length = length + 1

                if len(buffer) - cur < packet_length:
                    break

                packet = bytes(
                    buffer[cur:cur + packet_length]
                )
                #validate checksup
                if self._verify_checksum(packet):

                    self._log_packet(
                        "TT_RECV",
                        packet,
                    )
                    #process packet
                    await self._process_packet(packet)

                cur += packet_length

            if cur:
                del buffer[:cur]

    async def _process_packet(self, packet):

        _LOGGER.debug(
            "TT_LISTENER_ENTITIES=%s",
            len(self._listeners),
        )
        
        command = packet[2]

        if command != COMMAND_REPORT:
            return
        #get teletask device identity from the packet
        tt_cu = packet[3]
        tt_type = packet[4]
        tt_id = (packet[5] << 8) + packet[6]
        tt_state = packet[8]

        _LOGGER.debug(
            "TT_REPORT tt_cu=%s tt_type=%s tt_id=%s tt_state=%s",
            tt_cu,
            tt_type,
            tt_id,
            tt_state,
        )
        #acknowledge packet reception to teletask
        if self.writer:
            self.writer.write(bytes([COMMAND_ACK]))
            await self.writer.drain()

        _LOGGER.debug("TT_BEFORE_CALLBACK")
        
        if self._event_callback:
            try:
                await self._event_callback(
                    tt_cu,
                    tt_type,
                    tt_id,
                    tt_state,
                )
            except Exception:
                _LOGGER.exception(
                    "TT_EVENT_CALLBACK_FAILED"
                )
            
        #notify listener to update information in HA
        _LOGGER.debug("TT_BEFORE_LISTENERS")

        key = (
            tt_cu,
            tt_type,
            tt_id,
        )

        listener = self._listeners.get(key)

        if listener:
            try:
                listener(
                    tt_cu,
                    tt_type,
                    tt_id,
                    tt_state,
                )
            except Exception:
                _LOGGER.exception(
                    "TT_LISTENER_FAILED"
                )
        
    async def _send(self, packet):

        async with self._send_lock:

            self._ack_waiter = asyncio.Event()

            self._log_packet(
                "TT_SEND",
                packet,
            )

            if self.writer is None:
                raise ConnectionError(
                    "Teletask socket not connected"
                )

            self.writer.write(packet)
            await self.writer.drain()
            #wait 1s for teletask confirmation otherwise timeout
            try:
                await asyncio.wait_for(
                    self._ack_waiter.wait(),
                    timeout=1.0,
                )

                _LOGGER.debug(
                    "TT_ACK_OK"
                )

            except asyncio.TimeoutError:

                _LOGGER.warning(
                    "TT_ACK_TIMEOUT"
                )

            finally:
                self._ack_waiter = None

    def _build_packet(
    #builds packet as required by teletask api
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
    #update information/change state in teletask
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
