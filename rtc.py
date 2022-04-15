import uuid
import logging
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay, MediaRecorder, MediaBlackhole
from video_transform_track import VideoTransformTrack

pcs = set()
pc_logger = logging.getLogger("peer_connection")
relay = MediaRelay()
record_to = None
dc = None


async def connect(request):
    parmas = await request.json()
    offer = RTCSessionDescription(sdp=parmas["sdp"], type=parmas["type"])
    pc = RTCPeerConnection()
    
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        pc_logger.info(pc_id+" "+msg, *args)
    log_info("created for %s", request.remote)

    if record_to is not None:
        recorder = MediaRecorder(record_to)
    else:
        recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        global dc
        dc = channel

        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong"+message[4:1])

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            logging.info("connection lost")
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        if record_to is not None:
            # 录视频
            pc_logger.info("start to record " + record_to)
            recorder.addTrack(relay.subscribe(track))
            
        logging.info(parmas["constraints"])
        pc.addTrack(VideoTransformTrack(parmas["constraints"]["video"],relay.subscribe(track)))

        @track.on("ended")
        async def on_ended():
            if record_to is not None:
                pc_logger.info("stop to record " + record_to)
            recorder.stop

    await recorder.start()
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return pc