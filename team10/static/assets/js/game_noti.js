//----------------1시간마다 스트레칭 알람----------------
let globalstretchingNotification = null;

// 알림 생성 함수
function makeGameNoti() {
    // 이미 알림이 활성화되어 있다면 새 알림을 생성하지 않음
    if (globalstretchingNotification) {
        return;
    }
    // 권한이 허용된 경우에만 알림 생성
    if (Notification.permission === "granted") {
        globalstretchingNotification = new Notification("스트레칭 알림 (바른자세 도우미)", {
            body: "스트레칭 할 시간입니다. \n찌뿌둥한 몸을 풀어보는게 어떨까요?",
            icon: gameiconUrl,
            requireInteraction: true, // 사용자 상호작용이 필요
        });

        // 알림 클릭 이벤트 처리
        globalstretchingNotification.addEventListener("click", () => {
            window.location.href = "http://localhost:8000/service/game/";
            globalstretchingNotification.close();
            globalstretchingNotification = null; // 전역 알림 객체 초기화
        });
    }
}

// 알림 닫기 함수
function closeStretchingNotification() {
    if (globalstretchingNotification) {
        globalstretchingNotification.close();
        globalstretchingNotification = null; // 전역 알림 객체 초기화
    }
}

// 전역 스코프에서 함수 사용 가능하도록 설정
window.makeGameNoti = makeGameNoti;
window.closeStretchingNotification = closeStretchingNotification;
