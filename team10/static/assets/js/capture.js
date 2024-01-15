//----------------------알림 설정---------------------------------

let badPostureCount = 0; // 나쁜 자세 카운트
let goodPostureCount = 0; // 좋은 자세 카운트
let notificationActive = false;  // 알림 활성화 상태

function updatePostureStatusCounts(class_name) {
  // 나쁜 자세 카운트 증가 (0과 -1을 제외한 모든 경우)
  if (class_name !== 0 && class_name !== -1) {
      badPostureCount++;
      goodPostureCount = 0; // 나쁜 자세가 감지되면 좋은 자세 카운트 리셋
  } else if (class_name === 0) {
      // 좋은 자세가 감지되면 좋은 자세 카운트 증가, 나쁜 자세 카운트 리셋
      goodPostureCount++;
      badPostureCount = 0;
  } else {
      // 감지 불가 상태가 나오면 모든 카운트 리셋
      badPostureCount = 0;
      goodPostureCount = 0;
  }

  // 연속된 나쁜 자세 감지 (1분 동안 누적) => 20으로 바꾸기
  if (badPostureCount === 3 && !notificationActive) {
      makeNoti();  // 알림 생성
      notificationActive = true;
  }

  // 연속된 좋은 자세 감지 => 4로 바꾸기 (12초)
  if (goodPostureCount === 2 && notificationActive) {
      closeNotification();  // 알림 종료
      notificationActive = false;
  }
}

//----------------------------웹캠 설정-------------------------------
    
    var width = 720;    
    var height = 0;    
  
    var streaming = false;
  
    var video = null;
    var canvas = null;
    var photo = null;
    var startbutton = null;
    var sendImg = null;
    var myTracks = null;
    var streamingStatus = false;
  
    function startup() {
      video = document.getElementById('video');
      canvas = document.getElementById('canvas');
      photo = document.getElementById('photo');
      startbutton = document.getElementById('startbutton');
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
          height = 407;
        
          if (isNaN(height)) { //높이가 계산되지 않는 경우 
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
        askNotificationPermission();
        startVideo();
        ev.preventDefault();
      }, false);

      stopbutton.addEventListener('click', function(ev){
        var videoElement = document.getElementById('video');
        jQuery("#posture-status").html('');
        videoElement.style.boxShadow = "";
        videoElement.style.border = '';
        closeNotification();
        closeStretchingNotification();
        ev.preventDefault();
        stopVideo(); //위치 중요 //true여야 실행됨
      }, false);


      clearphoto();
    } 

    function to_statistics(){
      window.location.href = "http://localhost:8000/service/statistics";
    }

    function stopVideo() {
      if(streamingStatus){
        video.srcObject.getTracks().forEach( (track) => {
          track.stop();
          });
        clearInterval(sendImg);
        clearInterval(sendGameNoti);

        streamingStatus = false;
        to_statistics();
      }
    }
    

    function startVideo() {
      video.play();
      streamingStatus = true;
      sendImg = setInterval(sendImage, 3000);
      sendGameNoti = setInterval(makeGameNoti, 20000); //스트레칭 알림 20초 설정 -> 1시간으로 바꿀 예정
    }
  
    function clearphoto() {
      var context = canvas.getContext('2d');
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);
  
      var data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
    }
    

    function isBadPosture(num){
      let videoElement = document.getElementById('video');
      updatePostureStatusCounts(num);
      if (num==0) {
        videoElement.style.boxShadow = "0 0 8px 3px rgba(50, 205, 50, 0.7)";
        videoElement.style.border = '3px solid lime';
        document.getElementById('posture-status').style.color = 'lime'; 
        return 'Good Posture';
      } 
      if(num==-1){
        videoElement.style.boxShadow = "";
        videoElement.style.border = '';
        document.getElementById('posture-status').style.color = 'blue';
        return 'Unable to detect posture';
      }
      else {
        videoElement.style.boxShadow = "0 0 15px 5px rgba(255, 0, 0, 0.7)";
        videoElement.style.border = '3px solid red';
        document.getElementById('posture-status').style.color = 'red';
        return 'Bad Posture';
      }
    }

    function sendImage() {
      var context = canvas.getContext('2d');
      canvas.width = width;
      canvas.height = height;

      context.translate(video.width, 0);
      context.scale(-1, 1);
      context.drawImage(video, 0, 0, width, height);

      var picdata = canvas.toDataURL('image/png');
      photo.setAttribute('src', picdata);

      canvas.toBlob(blob => {
        const jpegBlob = new Blob([blob], { type: 'image/png' });
        const fileName = 'canvas_img_' + new Date().getMilliseconds() + '.png';
        var data = new FormData($('form')[0]);
        // var picdata = canvas.toDataURL('image/png');
        data.append("img_file", jpegBlob, fileName);

        $.ajax({
          type : "POST",
          url : "/service/send_image/", // 통신할 url을 지정
          // enctype : "multipart/form-data",
          processData : false,
          contentType : false,
          data: data,
          datatype: 'json',
          success: function (data) {
            jQuery("#posture-status").html(isBadPosture(Number(data['class_name'])));
          },
          error: function(e){
          }
        });
      }, 'image/png');
    } 


    window.addEventListener('load', startup, false);

