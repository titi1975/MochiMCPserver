# pip install mcp httpx
import os
import httpx
from mcp.server import MCPServer

mcp = MCPServer("mochi-flashcards")

MOCHI_BASE = "https://app.mochi.cards/api"
API_KEY = os.environ["MOCHI_API_KEY"]

def mochi() -> httpx.Client:
    return httpx.Client(base_url=MOCHI_BASE, auth=(API_KEY, ""))

#decks
@mcp.tool()
def list_decks() -> list[dict]:
    """Lista todos os decks do Mochi."""
    with mochi() as c:
        r = c.get("/decks/")
        r.raise_for_status()
        return r.json()["docs"]  # resposta vem paginada: {"bookmark", "docs": [...]}

@mcp.tool()
def create_deck(name:str,parentid:str | None = None) -> dict:
    """Cria um deck novo no mochi"""

    payload = {
        "name":name
    }
    if parentid:
        payload["parent-id"] = parentid
    with mochi() as c:
        r = c.post("/decks/", json=payload)
        r.raise_for_status()
        return r.json()

def delete_deck(deckid:str) -> str:
    """apaga um deck do mochi"""

    with mochi() as c:
        r = c.delete(f"/decks/{deckid}")
        r.raise_for_status()
        return f"deck {deckid} foi deletada com sucesso"
        
#cards
@mcp.tool()
def create_card(content: str,deckid:str,templateid:str, fields: dict[str, str]) -> dict:
    """Cria uma carta nova no mochi"""
    #criar catas sem template depois
    with mochi() as c:
        r = c.post("/cards/", json={"content":content,
                                    "deck-id":deckid,
                                    "template-id":templateid,
                                    "fields":{
                                        field_id: {"id": field_id, "value": value}
                                        for field_id, value in fields.items()
                                    }})
        r.raise_for_status()
        return r.json()

@mcp.tool()
def delete_card(cardid:str) -> str:
    """Apaga uma carta no mochi"""

    with mochi() as c:
        r = c.delete(f"/cards/{cardid}")
        r.raise_for_status()
        return f"carta {cardid} foi deletada com sucesso"

@mcp.tool()
def list_cards(deckid:str | None = None) -> list[dict]:
    """Lista as cartas e pode listar as cartas de um deck especifico no mochi"""

    all_cards = []
    params = {}
    bookmark = None

    if deckid:
        params["deck-id"] = deckid

    with mochi() as c:
        while True:

            if bookmark:
                    params["bookmark"] = bookmark
            r = c.get("/cards/",params=params)
            r.raise_for_status()
            data = r.json()

            cards_page = data.get("docs",[])
            all_cards.extend(cards_page)

            bookmark = data.get("bookmark")

            if params.get("bookmark") == data.get("bookmark"):
                break

        return all_cards
                
# POST https://app.mochi.cards/api/cards/

#templates
@mcp.tool()
def list_templates() -> list[dict]:
    """Lista todos os templates do baixados no mochi"""
    with mochi() as c:
        r = c.get("/templates/")
        r.raise_for_status()
        return r.json()["docs"]

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))