# this is an small discord multitoken vc joiner with streaming status, i made this while bored have fun with this!
# made by jinx
import os
import asyncio
import aiohttp
import websockets
import json
import colorama
from colorama import Fore, Style
import platform
import ctypes
import sys
colorama.init()
LOGO = f"""
{Fore.RED} ‎ ‎ ‎ ‎ ‎ ‎ ‎‎ ‎  ‎ ‎ ‎‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎      ██╗██╗███╗   ██╗██╗  ██╗███████╗██████╗     ████████╗ ██████╗  ██████╗ ██╗
 ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎ ‎ ‎      ██║██║████╗  ██║╚██╗██╔╝██╔════╝██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
 ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎‎ ‎ ‎ ‎ ‎ ‎      ██║██║██╔██╗ ██║ ╚███╔╝ █████╗  ██║  ██║       ██║   ██║   ██║██║   ██║██║
 ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎‎ ‎ ‎ ‎ ‎ ‎ ██   ██║██║██║╚██╗██║ ██╔██╗ ██╔══╝  ██║  ██║       ██║   ██║   ██║██║   ██║██║
 ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎‎  ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎ ‎ ‎ ╚█████╔╝██║██║ ╚████║██╔╝ ██╗███████╗██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗
 ‎ ‎ ‎ ‎ ‎   ‎‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎ ‎  ╚════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
{Style.RESET_ALL}
"""
ws_connections = {}
token_tasks = {}
def refresh_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(LOGO)
def set_window_title(title):
    if platform.system() == "Windows":
        ctypes.windll.kernel32.SetConsoleTitleW(title)
    elif platform.system() in ["Linux", "Darwin"]:
        sys.stdout.write(f"\x1b]2;{title}\x07")
        sys.stdout.flush()
async def heartbeat(ws, interval):
    while True:
        try:
            await asyncio.sleep(interval)
            await ws.send(json.dumps({"op": 1, "d": None}))
        except websockets.ConnectionClosed:
            break
async def connect_voice_channel(token, voice_channel_id, guild_id, self_mute, self_deaf, screenshare, streaming_status=None):
    while True:
        headers = {"Authorization": token, "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com/api/v9/gateway", headers=headers) as resp:
                if resp.status != 200:
                    await asyncio.sleep(10)
                    continue
                ws_url = (await resp.json())["url"]
        try:
            ws = await websockets.connect(f"{ws_url}/?v=9&encoding=json", max_size=None)
            ws_connections[token] = ws
            await ws.send(json.dumps({
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "Windows", "$browser": "Chrome", "$device": "PC"}
                }
            }))
            if (response := json.loads(await ws.recv()))['op'] == 10:
                asyncio.create_task(heartbeat(ws, response['d']['heartbeat_interval'] / 1000))
            while (response := json.loads(await ws.recv()))['op'] != 0 or response['t'] != 'READY':
                pass
            if streaming_status:
                await ws.send(json.dumps({
                    "op": 3,
                    "d": {
                        "since": None,
                        "activities": [{
                            "name": streaming_status,
                            "type": 1,
                            "url": "https://www.twitch.tv/your_stream"
                        }],
                        "status": "online",
                        "afk": False
                    }
                }))
            await ws.send(json.dumps({
                "op": 4,
                "d": {
                    "guild_id": str(guild_id),
                    "channel_id": str(voice_channel_id),
                    "self_mute": self_mute,
                    "self_deaf": self_deaf,
                    "self_video": screenshare
                }
            }))
            await asyncio.sleep(100)
            await ws.close()
        except websockets.ConnectionClosed:
            await asyncio.sleep(10)
def get_tokens():
    with open("tokens.txt", "r") as file:
        return [line.strip() for line in file.readlines()]
async def main():
    set_window_title("Jinx's VC Joiner")
    refresh_screen()
    tokens = get_tokens()
    streaming_status = None
    while (user_input := input(f"{Fore.RED}Do you want to set a streaming status on tokens? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()) not in ["yes", "y", "no", "n"]:
        print(f"{Fore.YELLOW}Invalid input. Please enter 'yes/y' or 'no/n'.{Style.RESET_ALL}")
    if user_input in ["yes", "y"]:
        streaming_status = input(f"{Fore.RED}Enter the streaming status text: {Style.RESET_ALL}")
        refresh_screen()
    guild_id = input(f"{Fore.RED}Enter the server (guild) ID: {Style.RESET_ALL}")
    refresh_screen()
    voice_channel_id = input(f"{Fore.RED}Enter the voice channel ID: {Style.RESET_ALL}")
    refresh_screen()
    while (mute_input := input(f"{Fore.RED}Should tokens be muted? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()) not in ["yes", "y", "no", "n"]:
        print(f"{Fore.YELLOW}Invalid input. Please enter 'yes/y' or 'no/n'.{Style.RESET_ALL}")
    self_mute = mute_input in ["yes", "y"]
    while (deaf_input := input(f"{Fore.RED}Should tokens be deafened? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()) not in ["yes", "y", "no", "n"]:
        print(f"{Fore.YELLOW}Invalid input. Please enter 'yes/y' or 'no/n'.{Style.RESET_ALL}")
    self_deaf = deaf_input in ["yes", "y"]
    while (screenshare_input := input(f"{Fore.RED}Should tokens enable screenshare? (yes/y/no/n): {Style.RESET_ALL}").strip().lower()) not in ["yes", "y", "no", "n"]:
        print(f"{Fore.YELLOW}Invalid input. Please enter 'yes/y' or 'no/n'.{Style.RESET_ALL}")
    screenshare = screenshare_input in ["yes", "y"]
    refresh_screen()
    tasks = [asyncio.create_task(connect_voice_channel(token, voice_channel_id, guild_id, self_mute, self_deaf, screenshare, streaming_status)) for token in tokens]
    for token, task in zip(tokens, tasks):
        token_tasks[token] = task
    try:
        await asyncio.gather(*token_tasks.values())
    except KeyboardInterrupt:
        for task in token_tasks.values():
            task.cancel()
        for ws in ws_connections.values():
            await ws.close()
if __name__ == "__main__":
    asyncio.run(main())
# if you give credit, you can take parts of the code :3
