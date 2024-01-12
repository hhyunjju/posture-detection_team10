 
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
            height = video.videoHeight / (video.videoWidth/width);
          
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
    
        stretchingGame();

        clearphoto();
    }


    function to_service(){
      window.location.href = "http://localhost:8000/service/service";
    }

    function startVideo() {
      video.play();
      streamingStatus = true;
      jQuery("#bigcount").hide();
    }

    function stopVideo() {
      if(streamingStatus){
        video.srcObject.getTracks().forEach( (track) => {
          track.stop();
          });''
        streamingStatus = false;
        to_service();
      }
    }

    function clearphoto() {
      var context = canvas.getContext('2d');
      context.fillStyle = "#AAA";
      context.fillRect(0, 0, canvas.width, canvas.height);
  
      var data = canvas.toDataURL('image/png');
      photo.setAttribute('src', data);
    }
    


    let answer = [];

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
        data.append("img_file", jpegBlob, fileName);
        

        $.ajax({
          type : "POST",
          url : "/service/send_image_game/", // 통신할 url을 지정
          processData : false,
          contentType : false,
          data: data,
          datatype: 'json',
          success: function (data) {
            if (jQuery("#posture-status").html()==data['class_name']) {
              answer.push(1);
            }
            else {
              answer.push(0);
            }
          },
          error: function(e){
            console.log('error');
          }
        });
      }, 'image/png');
      console.log(streaming);
    }

// ----------------------- Timer ----------------------------------
//10초에 사용하는 타이머(스트레칭)
    function TIMER(time, min, sec){
      PLAYTIME=setInterval(function(){
            time=time-1000; //1초씩 줄어듦
            min=time/(60*1000); //초를 분으로 나눠준다.
    
           if(sec>0){ //sec=60 에서 1씩 빼서 출력해준다.
                sec=sec-1;
                jQuery("#count").html(sec);//화면에 표시
               
            }
            if(sec===0){
               // 0에서 -1을 하면 -59가 출력된다.
                // 그래서 0이 되면 바로 sec을 60으로 돌려주고 value에는 0을 출력하도록 해준다.
                sec=60;
                jQuery("#count").html('0');
            }    
            if($('#count').html()=='0'){
                jQuery("#count").html('<i class="fa-solid fa-hourglass-end"></i>');
            } 
        
        },1000); //1초마다 
    }

//5초에 사용하는 타이머(대기)
//TIMER FOR BIGCOUNT
function BIGTIMER(time, min, sec){
  PLAYTIME=setInterval(function(){
        time=time-1000; //1초씩 줄어듦
        min=time/(60*1000); //초를 분으로 나눠준다.

       if(sec>0){ //sec=60 에서 1씩 빼서 출력해준다.
            sec=sec-1;
            jQuery("#bigcount").html(sec);//화면에 표시
           
        }
        if(sec===0){
           // 0에서 -1을 하면 -59가 출력된다.
            // 그래서 0이 되면 바로 sec을 60으로 돌려주고 value에는 0을 출력하도록 해준다.
            sec=60;
            jQuery("#bigcount").html('0');
        }    
        if($('#bigcount').html()=='0'){
          jQuery("#bigcount").html('START');
        } 
    
    },1000); //1초마다 
}

    //5초에 사용하는 함수
    function myTimer(sen, time, m, s) {
      return new Promise(resolve => {
        jQuery("#bigcount").html(s);
        jQuery("#subscription").html(sen);
        BIGTIMER(time,m,s);
        setTimeout(() => {
          clearInterval(PLAYTIME);
          resolve();
      }, time);
      });
    }

    //------------10초에 사용하는 함수
    //------------- myTimer2 수정(progressbar 포함 & sendimg)
    function myTimerWithProgressBar(sen, time, m, s) {
      return new Promise(resolve => {
        jQuery("#successcount").empty();
        jQuery("#count").html(s);
        jQuery("#subscription").html(sen);
        TIMER(time, m, s);
    
        let progressBarElement = document.getElementById("progressBar");
        let startProgressBarTime = Date.now();
    
        function updateProgressBar() {
          let currentTime = Date.now();
          let elapsedTime = currentTime - startProgressBarTime;
          let progress = (elapsedTime / time) * 100;
          progressBarElement.style.width = progress + "%";
    
          if (elapsedTime < time) {
            requestAnimationFrame(updateProgressBar);
          } else {
            progressBarElement.style.width = "100%";
          }
        }
    
        requestAnimationFrame(updateProgressBar);
        var sendimg = setInterval(sendImage, 1000);
    
        setTimeout(() => {
          clearInterval(sendimg);
          clearInterval(PLAYTIME);
          resolve();
        }, time);
      });
    }
    

    //--------------------------------------------------------
    function mySendImage(){
      return new Promise(resolve => {
        sendImage();
        resolve();
      });
    }

    function myStartVideo(){
      return new Promise(resolve => {
        setTimeout(() => {
          startVideo();
          resolve();
      }, 700);
      });
    }

    function myStopVideo(){
      return new Promise(resolve => {
        jQuery("#successcount").html('SUCCESS');
        setTimeout(() => {
          stopVideo();
          resolve();
      }, 3000);
      });
    }

    function tryAgain() {
      return new Promise(resolve => {
        var sentence = '맞을 때까지 나갈 수 없습니다.\n 다시 해 보세요';
        jQuery("#subscription").html(sentence);
        jQuery("#successcount").html("Time's Up");
        answer = [];
        failSignal();
        resolve();
      });
    }

    var stretchingAgain = false;

    function myAnswer() {
      return new Promise(resolve => {
        if(answer.indexOf(1)==-1){
          $('#stretchingStatus').html('X');
          stretchingAgain = true;
        } else if (answer.indexOf(1)>=0){
          stretchingAgain = false;
          $('#stretchingStatus').html('O');
        }
        resolve();
      });
    }

    function sleep(ms){
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    async function stretchingGame(){
      await myTimer('5초 뒤에 스트레칭이 시작됩니다.', 5000, 0, 5);
      await myStartVideo();
      await myTimerWithProgressBar('왼쪽의 동작을 10초 동안 따라해주세요.', 10000, 0, 10);
      await myAnswer();
      while(stretchingAgain){
        await tryAgain();
        await sleep(1500);
        await myTimerWithProgressBar('왼쪽의 동작을 10초 동안 다시 따라해주세요.', 10000, 0, 10);
        await myAnswer();
      }
      await myStopVideo();
    }

    window.addEventListener('load', startup, false);

