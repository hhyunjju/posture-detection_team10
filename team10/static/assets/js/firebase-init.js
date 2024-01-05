// Firebase 구성 객체
const firebaseConfig = {
    apiKey: "AIzaSyBRL-Vcf1dUF9XtauIMrYIIPFAPO7zT4-8",
    authDomain: "aivle-team10.firebaseapp.com",
    projectId: "aivle-team10",
    messagingSenderId: "531835039253",
    appId: "1:531835039253:web:79a1ad72c872e6a6e3681c",
    measurementId: "G-B3S2T2QLR7"
  };
  
  // Firebase 초기화
  firebase.initializeApp(firebaseConfig);
  
  // 메시징 객체 얻기
  const messaging = firebase.messaging();
  // 서비스 워커 등록
  navigator.serviceWorker.register('/firebase-messaging-sw.js')
  .then((registration) => {
    messaging.useServiceWorker(registration);
  });
  // 사용자가 푸시 알림을 구독하도록 요청 & FCM 토큰을 얻기
  messaging.requestPermission() //푸시 알림 권한 요청
  .then(function() {
    return messaging.getToken(); //Firebase가 FCM 토큰 생성 -> 받기
  })
  .then(function(token) { // 토큰을 서버로 전송
    console.log("Received FCM Token:", token);
    // 여기에 서버로 토큰을 전송하는 AJAX 요청 추가
    $.ajax({
      url: '/save-fcm-token/', // 서버 엔드포인트 URL
      type: 'POST',
      headers: {
        'X-CSRFToken': csrfToken // CSRF 토큰 (필요한 경우)
      },
      data: {
        fcm_token: token
      },
      success: function(response) {
        console.log('FCM 토큰이 서버에 성공적으로 전송되었습니다.');
      },
      error: function(xhr, status, error) {
        console.error('FCM 토큰 전송 실패:', error);
      }
    });

  }) //
  .catch(function(err) {
    console.log('Permission denied', err);
  });
