import asyncio


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

        print(f"Connected to {self.host}:{self.port}")

    async def disconnect(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def get_relay_state(self, central_unit, relay_id):
        """
        Placeholder.
        Will later send FunctionGet command.
        """
        print(
            f"Read relay {relay_id} "
            f"on central {central_unit}"
        )

        return False

    async def set_relay_state(
        self,
        central_unit,
        relay_id,
        state
    ):
        """
        Placeholder.
        Will later send FunctionSet command.
        """
        print(
            f"Set relay {relay_id} "
            f"on central {central_unit} "
            f"to {state}"
        )
``