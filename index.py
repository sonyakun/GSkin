from typing import Union
import httpx, base64, json
from fastapi import FastAPI, Depends
import uvicorn
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

description = """
GSkin is an API that simplifies the process of obtaining skin URLs from api.geysermc.org.
※It does not matter GSkin of Spigot Plugin.
"""

app = FastAPI(
    title="GSkin",
    description=description,
    version="0.0.1",
    contact={
        "name": "sonyakun",
        "url": "https://github.com/sonyakun/",
    },
    license_info={
        "name": "GNU General Public License v3.0",
        "url": "https://www.gnu.org/licenses/gpl-3.0.txt",
    },
)

@app.get("/decode/{b64_encoded}", description="base64 decoder")
def read_root(b64_encoded: bytes):
    return {"status": 200, "content": json.loads(base64.b64decode(b64_encoded).decode())}

@app.get("/skin/{mcid}", description="get bedrock skin")
def read_item(mcid: str):
    try:
        r1 = httpx.get(f"https://api.geysermc.org/v2/xbox/xuid/{mcid}")
        r1_json = r1.json()
        if not r1.status_code == 200:
            return {"status": 400, "message": "Failed to retrieve xuid.", "about": {"source": "https://github.com/sonyakun/gskin", "admin twitter": {"main": "https://twitter.com/sonyakun1", "en": "https://twitter.com/sonyakun2"}}}
        else:
            xuid = r1_json["xuid"]
        r2 = httpx.get(f"https://api.geysermc.org/v2/skin/{xuid}")
        if not r2.status_code == 200:
            return {"status": 400, "message": "Failed to retrieve minecraft skin."}
        else:
            resp = r2.json()
            skinA = resp["value"]
            skin = json.loads(base64.b64decode(skinA).decode())
            return {"status": 200, "content": {"hash": resp["hash"], "is_steve": resp["is_steve"], "last_update": resp["last_update"], "signature": resp["signature"], "texture_id": resp["texture_id"], "value": skin}}
    except Exception as e:
        return {"status": 500, "message": "internal server error", "error": e}

if __name__ == "__main__":
    uvicorn.run(app, port=8080)
