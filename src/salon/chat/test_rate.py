"""Test when/if we will get rate limited by youtube."""
import asyncio
import time

import requests

from salon.chat.chatbot import get_response


def _get_pokemons(url):
    res = requests.get(url).json()
    pokemons = [pok["name"] for pok in res["results"]]
    
    for pok in pokemons:
        yield pok

    return res["next"]

def get_pokemons():
    url = "https://pokeapi.co/api/v2/pokemon"
    while url:
        pokemons = _get_pokemons(url)
        try:
            while True:
                yield next(pokemons)
        except StopIteration as err:
            url = err.value

async def main():
    for i, pok in enumerate(get_pokemons()):
        print("Starting for pokemon", pok, "\n")
        start = time.perf_counter()
        resp = await get_response(pok)
        print(f"{i}, TOOK: {time.perf_counter() - start:.2f}s")
        print("\n", resp, "\n")
        print("Sleeping...\n\n")
        time.sleep(10)  # Assume users don’t use it more than that, relevant for our setting

if __name__ == "__main__":
    print('Starting "benchmark"')
    asyncio.run(main())
