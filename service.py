import json
from aiohttp import web
import os
import rtc

ROOT = os.path.dirname(__file__)


async def index(_):
    content = open(os.path.join(ROOT, "client/index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def clentjs(_):
    content = open(os.path.join(ROOT, "client/client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

async def opencvjs(_):
    content = open(os.path.join(ROOT, "client/opencv.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)


async def alert_audio(_):
    content = open(os.path.join(ROOT, "./resource/alert.mp3"), "rb").read()
    return web.Response(content_type="audio/mpeg", body=content)

# webRTC 连接请求


async def offer(request):
    pc = await rtc.connect(request)
    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        )
    )