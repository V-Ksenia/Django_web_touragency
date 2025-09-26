const hourTimer = document.getElementById("countdown");


function formatTime(time) {
    const hours = Math.floor(time / 3600);
    const minutes = Math.floor((time % 3600) / 60);
    const seconds = time % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
} //формат 00:00:00


function startCountdown() {
    let endTime = localStorage.getItem("countdownEndTime");
    if (!endTime) {
        const now = new Date();
        endTime = new Date(now.getTime() + 3600 * 1000); // 1 час
        localStorage.setItem("countdownEndTime", endTime);
    } else {
        endTime = new Date(endTime);
    }

    const interval = setInterval(() => {
        const now = new Date();
        const timeLeft = Math.floor((endTime - now) / 1000); // оставшееся время в сек
        //время истекло
        if (timeLeft <= 0) {
            clearInterval(interval);
            hourTimer.textContent = "Time's up!";
            localStorage.removeItem("countdownEndTime"); 
        } else {
            hourTimer.textContent = formatTime(timeLeft);
        }
    }, 1000);
}


startCountdown();

