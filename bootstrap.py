import argparse
import asyncio
import logging
import ssl
from aiohttp import web
import service
import rtc


async def on_shutdown(app):
    # 关闭连接
    closes = [pc.close() for pc in rtc.pcs]
    await asyncio.gather(*closes)
    rtc.pcs.clear()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 使用https协议（webRTC）
    parser.add_argument("--cert-file", default="ssl/server.crt")
    parser.add_argument("--key-file", default="ssl/server_nopass.key")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default="8080")
    parser.add_argument("--record_to")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    logging.info(args)
    ssl_context = ssl.SSLContext()
    ssl_context.load_cert_chain(args.cert_file, args.key_file)
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    rtc.record_to = args.record_to
    app.router.add_get("/", service.index)
    app.router.add_get("/client.js", service.clentjs)
    app.router.add_post("/offer", service.offer)
    app.router.add_get("/resource/alert.mp3", service.alert_audio)

    web.run_app(app, access_log=None, host=args.host,
                port=args.port, ssl_context=ssl_context)
