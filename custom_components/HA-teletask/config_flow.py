from homeassistant import config_entries


class HATeletaskConfigFlow(
    config_entries.ConfigFlow,
    domain="ha_teletask",
):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(
            title="HA-Teletask",
            data={}
        )