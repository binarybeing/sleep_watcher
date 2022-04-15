
window.onclose = stop;
// peer connection
var pc = null;
// data channel
var dc = null;
var constraints = {
    audio: false,
    video: {width:320, height:240}
};
function start() {
    document.getElementById("start_button").hidden = true;
    createPeerConnection();
    init_audio();
    try {
        if (navigator.getUserMedia) {
            navigator.getUserMedia(constraints, successFunc, errorFunc);
        }
        else if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia(constraints).then(successFunc).catch(errorFunc);
        } else {
            alert('Native device media streaming (getUserMedia) not supported in this browser.');
        }
    } catch (err) {
        alert(err);
    }
}

function createPeerConnection() {
    var config = { sdpSemantics: 'unified-plan' };
    pc = new RTCPeerConnection(config);
    dc = pc.createDataChannel('chat', { "ordered": true });
    pc.ontrack = function(ent) {
        document.getElementById("server_video").srcObject = ent.streams[0]
    }
    dc.onmessage = function (evt) {
        if (evt.data.substring(0, 5) === 'alert') {
            wakeup_alert();
            return;
        }
        if (evt.data.substring(0, 4) === 'ping') {
            dc.send("pong")
            return;
        }
        var message = JSON.parse(evt.data);
        console.log(message);
    }

}

function negotiate() {
    return pc.createOffer().then(function (offer) {

        return pc.setLocalDescription(offer);
    }).then(function () {
        // wait for ICE gathering to complete
        return new Promise(function (resolve) {
            if (pc.iceGatheringState === 'complete') {
                resolve();
            } else {
                function checkState() {
                    if (pc.iceGatheringState === 'complete') {
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function () {
        var offer = pc.localDescription;
        
        return fetch('/offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type,
                constraints: constraints
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function (response) {
        return response.json();
    }).then(function (answer) {
        return pc.setRemoteDescription(answer);
    }).catch(function (e) {
        alert(e);
    });
}

function successFunc(stream) {
    stream.getTracks().forEach(function (track) {
        pc.addTrack(track, stream);
    });
    var video = document.getElementById("local_video");
    video.srcObject = stream;
    video.play();
    return negotiate();
}

function errorFunc(err) {
    alert(err);
}

function stop() {
    // close data channel
    if (dc) {
        dc.close();
    }
    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function (transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }
    // close local audio / video
    pc.getSenders().forEach(function (sender) {
        sender.track.stop();
    });
    // close peer connection
    setTimeout(function () {
        pc.close();
    }, 500);
}

const alert_music = new Audio("./resource/alert.mp3");
function init_audio(){
    alert_music.play();
    alert_music.pause();
}

var alert_control = new Array();
function wakeup_alert() {
    let now =parseInt( Date.now() / 1000);
    if(alert_control.length == 0 || now - alert_control[0] >= 2){
        alert_control = new Array();
        alert_control.unshift(now);
        return;
    }
    if(now - alert_control[0] == 0){
        return;
    }
    alert_control.unshift(now);
    if(alert_control.length > 4){
        alert_music.play();
        alert_music.onended = function(){
            red_warning.style.animationName = "";    
        }
        var red_warning = document.getElementById("red_warning");
        red_warning.style.animationName = "alert";
        alert_control.pop();
    }
    
}