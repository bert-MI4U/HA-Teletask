class ha_light:
    def __init__(self, config, api):
        self.api = api

        self.name = config["name"]
        self.device = config["device"]
        self.room = config["room"]
        self.icon = config["icon"]

        self.central_unit = config["teletask"]["central_unit"]
        self.relay_id = config["teletask"]["teletask_id"]

        self.is_on = False

    async def update(self):
        self.is_on = await self.api.get_relay_state(
            self.central_unit,
            self.relay_id
        )

        print(
            f"{self.name}: "
            f"{'ON' if self.is_on else 'OFF'}"
        )

    async def turn_on(self):
        await self.api.set_relay_state(
            self.central_unit,
            self.relay_id,
            True
        )

    async def turn_off(self):
        await self.api.set_relay_state(
            self.central_unit,
            self.relay_id,
            False
        )