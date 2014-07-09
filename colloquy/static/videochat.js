  var socket = new WebSocket('ws://50.141.244.113:1337/');
  var stunServer = "stun.l.google.com:19302";
  var sourcevid = document.getElementById('sourcevid');
  var remotevid = document.getElementById('remotevid');
  var localStream = null;
  var remoteStream;
  var peerConn = null;
  var started = false;
  var isRTCPeerConnection = true;
  var mediaConstraints = {'mandatory': {
                            'OfferToReceiveAudio':true, 
                            'OfferToReceiveVideo':true }};
							
  var logg = function(s) { console.log(s); };


  // send the message to websocket server
  function sendMessage(message) {
	  var mymsg = JSON.stringify(message);
      logg("SEND: " + mymsg);
      socket.send(mymsg);
  }
 
 
  function createPeerConnection() {
	try {
      logg("Creating peer connection");
	  var servers = [];
	  servers.push({'url':'stun:' + stunServer});
	  var pc_config = {'iceServers':servers};	  
      peerConn = new webkitRTCPeerConnection(pc_config);
      peerConn.onicecandidate = onIceCandidate;
    } catch (e) {
	    try {
	      peerConn = new RTCPeerConnection('STUN ' + stunServer, onIceCandidate00);
	      isRTCPeerConnection = false;
	    } catch (e) {
	      logg("Failed to create PeerConnection, exception: " + e.message);
	    }
	}

    peerConn.onaddstream = onRemoteStreamAdded;
    peerConn.onremovestream = onRemoteStreamRemoved;
  }
 
 
 
  // when remote adds a stream, hand it on to the local video element
  function onRemoteStreamAdded(event) {
    logg("Added remote stream");
    remotevid.src = window.webkitURL.createObjectURL(event.stream);
  }
 
 
 
  function waitForRemoteVideo() {
    if (remoteStream.videoTracks.length === 0 || remotevid.currentTime > 0) {
      transitionToActive();
    } else {
      setTimeout(waitForRemoteVideo, 100);
    }
  }
  
  
  
  function transitionToActive() {
    remotevid.style.opacity = 1;
    card.style.webkitTransform = "rotateY(180deg)";
    setTimeout(function() { sourcevid.src = ""; }, 500);
    setStatus("<input type=\"button\" id=\"hangup\" value=\"Hang up\" onclick=\"onHangup()\" />");
  }
  
  
  
  // when remote removes a stream, remove it from the local video element
  function onRemoteStreamRemoved(event) {
    logg("Remove remote stream");
    remotevid.src = "";
  }
 
 
  function onIceCandidate(event) {
    if (event.candidate) {
      sendMessage({type: 'candidate',
                   label: event.candidate.sdpMLineIndex,
                   id: event.candidate.sdpMid,
                   candidate: event.candidate.candidate});
    } else {
      logg("End of candidates.");
    }
  }
 
 
 
  function onIceCandidate00(candidate, moreToFollow) {
    if (candidate) {
        sendMessage({type: 'candidate', label: candidate.label, candidate: candidate.toSdp()});
    }
    if (!moreToFollow) {
      logg("End of candidates.");
    }
  }
 
 
 
  // start the connection upon user request
  function connect() {
    if (!started && localStream) {
	  //document.getElementById('anim').style.visibility='visible';
	  console.log("Creating PeerConnection.");
      createPeerConnection();
      logg('Adding local stream...');
      peerConn.addStream(localStream);
      started = true;
      logg("isRTCPeerConnection: " + isRTCPeerConnection);
 
	  //create offer
      if (isRTCPeerConnection) {
        peerConn.createOffer(setLocalAndSendMessage, null, mediaConstraints);
      } else {
        var offer = peerConn.createOffer(mediaConstraints);
        peerConn.setLocalDescription(peerConn.SDP_OFFER, offer);
        sendMessage({type: 'offer', sdp: offer.toSdp()});
        peerConn.startIce();
      }
 
    } else {
      alert("Local stream not running yet.");
    }
  }
 
 
 
  // accept connection request
  socket.addEventListener("message", onMessage, false);
  function onMessage(evt) {
    logg("RECEIVED: " + evt.data);
    if (isRTCPeerConnection)
      processSignalingMessage(evt.data);
    else
      processSignalingMessage00(evt.data);
  }
 
 
 
  function processSignalingMessage(message) {
    var msg = JSON.parse(message);
 
    if (msg.type === 'offer') {
 
      if (!started && localStream) {
	    createPeerConnection();
	    logg('Adding local stream...');
	    peerConn.addStream(localStream);
	    started = true;
        logg("isRTCPeerConnection: " + isRTCPeerConnection);
 
 
        if (isRTCPeerConnection) {
          //set remote description
          peerConn.setRemoteDescription(new RTCSessionDescription(msg));
          //create answer
		  console.log("Sending answer to peer.");
          peerConn.createAnswer(setLocalAndSendMessage, null, mediaConstraints);
        } else {
          //set remote description
          peerConn.setRemoteDescription(peerConn.SDP_OFFER, new SessionDescription(msg.sdp));
          //create answer
          var offer = peerConn.remoteDescription;
          var answer = peerConn.createAnswer(offer.toSdp(), mediaConstraints);
		  console.log("Sending answer to peer.");
          setLocalAndSendMessage00(answer);
        }
	  }
 
    } else if (msg.type === 'answer' && started) {
      peerConn.setRemoteDescription(new RTCSessionDescription(msg));
    } else if (msg.type === 'candidate' && started) {
      var candidate = new RTCIceCandidate({sdpMLineIndex:msg.label, candidate:msg.candidate});
      peerConn.addIceCandidate(candidate);
    } else if (msg.type == 'chat'){
    	addChatMsg(msg.nick, msg.cid, msg.data);
    } 
	else if (msg.type === 'bye' && started) {
      onRemoteHangUp();
    }
  }
 
 
 
  function processSignalingMessage00(message) {
    var msg = JSON.parse(message);
 
    // if (msg.type === 'offer')  --> will never happened since isRTCPeerConnection=true initially
	if (msg.type === 'answer' && started) {
      peerConn.setRemoteDescription(peerConn.SDP_ANSWER, new SessionDescription(msg.sdp));
    } else if (msg.type === 'candidate' && started) {
      var candidate = new IceCandidate(msg.label, msg.candidate);
      peerConn.processIceMessage(candidate);
    } else if (msg.type === 'bye' && started) {
      onRemoteHangUp();
    }
  }
 
 
 
  function setLocalAndSendMessage(sessionDescription) {
    peerConn.setLocalDescription(sessionDescription);
    sendMessage(sessionDescription);
  }
 
 
 
  function setLocalAndSendMessage00(answer) {
    peerConn.setLocalDescription(peerConn.SDP_ANSWER, answer);
    sendMessage({type: 'answer', sdp: answer.toSdp()});
    peerConn.startIce();
  }
 
 
 
  function onRemoteHangUp() {
    logg("Remote Hang up.");
    closeSession();
  }
 
 
  function onHangUp() {
    logg("Hang up.");
	//document.getElementById('anim').style.visibility='hidden';
 	if (started) {
      sendMessage({type: 'bye'});
      closeSession();
    }
  }
 
 
 
  function closeSession() {
    peerConn.close();
    peerConn = null;
    started = false;
    remotevid.src = "";	
  }
 
 
  window.onbeforeunload = function() {
	if (started) {
      sendMessage({type: 'bye'});
    }
  }
 
 
  function startVideo() {
      // Replace the source of the video element with the stream from the camera
      try { 
        navigator.webkitGetUserMedia({audio: true, video: true}, successCallback, errorCallback);
      } catch (e) {
        navigator.webkitGetUserMedia("video,audio", successCallback, errorCallback);
      }
      function successCallback(stream) {
          sourcevid.src = window.webkitURL.createObjectURL(stream);
	      sourcevid.style.webkitTransform = "rotateY(180deg)";
          localStream = stream;
      }
      function errorCallback(error) {
          logg('An error occurred: [CODE ' + error.code + ']');
      }
  }
 
 
  function stopVideo() {
    sourcevid.src = "";
  }