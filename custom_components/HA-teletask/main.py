import asyncio
import json

from teletask_api import teletask_api
from ha_light import ha_light


async def main():
    with open("config.json", "r") as f:
        config = json.load(f)

    api = teletask_api(
        config["teletask"]["ip"],
        config["teletask"]["port"]
    )

    await api.connect()

    lights = []

    for asset in config["assets"]:
        if asset["component"] == "light":
            lights.append(ha_light(asset, api))

    for light in lights:
        await light.update()

    await api.disconnect()


if __name__ == "__main__":
    asyncio.run(main())