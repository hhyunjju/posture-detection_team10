

    // The width and height of the captured photo. We will set the
    // width to the value defined here, but the height will be
    // calculated based on the aspect ratio of the input stream.
  
    var width = 720;    // We will scale the photo width to this
    var height = 0;     // This will be computed based on the input stream
  
    // |streaming| indicates whether or not we're currently streaming
    // video from the camera. Obviously, we start at false.
  
    var streaming = false;
  
    // The various HTML elements we need to configure or control. These
    // will be set by the startup() function.
  
    var video = null;
    var canvas = null;
    var photo = null;
    var startbutton = null;
    var sendImg = null;
    var myTracks = null;
  
    function startup() {
      video = document.getElementById('video');
      canvas = document.getElementById('canvas');
      photo = document.getElementById('photo');
      startbutton = document.getElementById('startbutton');
      pausebutton = document.getElementById('pausebutton');
      stopbutton = document.getElementById('stopbutton');

      const constraints = {
        video: {
            frameRate: {
                ideal: 10, max: 15
            },
        }, 
        audio: false,
        };

        navigator.mediaDevices
        .getUserMedia(constraints)
        .then((mediaStream) => {
            video.srcObject = mediaStream;
            myTracks = video.srcObject.getTracks();
        })
        .catch((err) => {
            console.error(`${err.name}: ${err.message}`);
        });

        
  
        video.addEventListener('canplay', function(ev){
          if (!streaming) {
            height = video.videoHeight / (video.videoWidth/width);
          
            // Firefox currently has a bug where the height can't be read from
            // the video, so we will make assumptions if this happens.
          
            if (isNaN(height)) {
              height = width / (4/3);
            }
          
            video.setAttribute('width', width);
            video.setAttribute('height', height);
            canvas.setAttribute('width', width);
            canvas.setAttribute('height', height);
            streaming = true;
          }
        }, false);
    
        startbutton.addEventListener('click', function(ev){
          startVideo();
          ev.preventDefault();
        }, false);

        stopbutton.addEventListener('click', function(ev){
          stopVideo();
          ev.preventDefault();
        }, false);

        pausebutton.addEventListener('click', function(ev){
          pauseVideo(myTracks);
          ev.preventDefault();
        }, false);
        
        clearphoto();
    }


    function pauseVideo (track) {
      alert('아직 공사중.. 빠질 수 있음..');
    };


    function stopVideo() {
      video.srcObject.getTracks().forEach( (track) => {
        track.stop();
        });
      clearInterval(sendImg);
    }

    function startVideo() {
      video.play();
      sendImg = setInterval(sendImage, 3000);
    }


  
    // Fill the photo with an indication that none has been
    // captured.
  
    function clearphoto() {
      var context = canvas.getContext('2d');
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);
  
      var data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
    }
    
    // Capture a photo by fetching the current contents of the video
    // and drawing it into a canvas, then converting that to a PNG
    // format data URL. By drawing it on an offscreen canvas and then
    // drawing that to the screen, we can change its size and/or apply
    // other changes before drawing it.


    function sendImage() {
      var context = canvas.getContext('2d');
      canvas.width = width;
      canvas.height = height;
      // console.log(width);
      // console.log(height);
      context.drawImage(video, 0, 0, width, height);

      var picdata = canvas.toDataURL('image/png');
      photo.setAttribute('src', picdata);

      canvas.toBlob(blob => {
        const jpegBlob = new Blob([blob], { type: 'image/png' });
        const fileName = 'canvas_img_' + new Date().getMilliseconds() + '.png';
        // const formData = new FormData();
        // formData.append('camera-image', blob);
        var data = new FormData($('form')[0]);
        // var picdata = canvas.toDataURL('image/png');
        data.append("img_file", jpegBlob, fileName);
        console.log('form에 이미지 추가');

        

        $.ajax({
          type : "POST",
          url : "/service/send_image/", // 통신할 url을 지정
          // enctype : "multipart/form-data",
          processData : false,
          contentType : false,
          data: data,
          success: function (response) {
            console.log('success');
          },
          error: function(e){
            console.log('error');
          }
        });
      }, 'image/png');
      console.log(streaming);
    }

// var imageSrc = $("#previewImage").attr("src");
  
    // Set up our event listener to run the startup process
    // once loading is complete.
    window.addEventListener('load', startup, false);


      /* 
      let mediaRecorder;
      let recordedBlobs;
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      const video = document.getElementById('video');
      const startButton = document.getElementById('startRecording');
      const stopButton = document.getElementById('stopRecording');
      
      const constraints = {
        video: {
          frameRate: {
            ideal: 10, max: 15
          },
        }
      };

      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((mediaStream) => {
          video.srcObject = mediaStream;
        })
        .catch((err) => {
          console.error(`${err.name}: ${err.message}`);
        });

      function captureImage(){
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        canvas.toBlob(blob => {
          const formData = new FormData();
          formData.append('camera-image', blob);
          fetch('../../views/test/', {
            method: 'POST',
            body : formData
          });
        });
      }
      startButton.addEventListener('click', () => {
        startRecording();
      });

      stopButton.addEventListener('click', () => {
        stopRecording();
      });

      function startRecording() {
        recordedBlobs = [];
        let options = { mimeType: 'video/webm;codecs=vp9' };
        if (!MediaRecorder.isTypeSupported(options.mimeType)) {
          console.error(`${options.mimeType} is not supported`);
          options = { mimeType: 'video/webm;codecs=vp8' };
          if (!MediaRecorder.isTypeSupported(options.mimeType)) {
            console.error(`${options.mimeType} is not supported`);
            options = { mimeType: 'video/webm' };
          }
        }

        try {
          mediaRecorder = new MediaRecorder(window.stream, options);
        } catch (e) {
          console.error('Exception while creating MediaRecorder:', e);
          return;
        }

        startButton.disabled = true;
        stopButton.disabled = false;

        mediaRecorder.onstop = (event) => {
          console.log('Recorder stopped: ', event);
        };

        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            recordedBlobs.push(event.data);
          }
        };

        mediaRecorder.start();
        console.log('MediaRecorder started', mediaRecorder);
      }

      function stopRecording() {
        mediaRecorder.stop();
        startButton.disabled = false;
        stopButton.disabled = true;

        const blob = new Blob(recordedBlobs, { type: 'video/webm' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'recorded_video.webm';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => {
          document.body.removeChild(a);
          window.URL.revokeObjectURL(url);
        }, 100);
      }

      navigator.mediaDevices.getUserMedia({ audio: true, video: true })
        .then(stream => {
          window.stream = stream;
          video.srcObject = stream;
        })
        .catch(e => {
          console.error('getUserMedia() error:', e);
        });
  */