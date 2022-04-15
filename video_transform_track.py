
import logging
from re import X
from aiortc import MediaStreamTrack
import rtc
import json
import time
import train
import pickle
import numpy as np
import cv2
from av import VideoFrame

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
fgbg = cv2.bgsegm.createBackgroundSubtractorGMG(initializationFrames=5)

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"
    last_check = int(round(time.time() * 1000))

    def __init__(self, video, track):
        super().__init__()
        self.track = track
        self.video = video

    async def recv(self):
        frame = await self.track.recv()
        now = int(round(time.time() * 1000))
        if now - self.last_check <100:
            return frame
        self.last_check = now
        img = frame.to_ndarray(format="bgr24")
        fgmask = fgbg.apply(img)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)   # 过滤噪声
        (cnts, _) = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        alert = False
        for c in cnts:
            c_area = cv2.contourArea(c)
            if c_area < 600 :  # 过滤太小或太大的运动物体，这类误检概率比较高
                continue
            if c_area > 16000:
                alert = False
                break
            (x, y, w, h) = cv2.boundingRect(c)
            alert = True
            img = cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        if alert :
            rtc.dc.send("alert")
            
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame    