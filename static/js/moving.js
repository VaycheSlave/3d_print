// Получаем элементы интерфейса управления
const moveX-10mmButton = document.getElementById('move-x-10mm');
const moveX-100mmButton = document.getElementById('move-x-100mm');
const moveX+10mmButton = document.getElementById('move-x+10mm');
const moveX100mmButton = document.getElementById('move-x-100mm');
const moveY10mmButton = document.getElementById('move-y-10mm');
const moveY100mmButton = document.getElementById('move-y-100mm');
const moveZ10mmButton = document.getElementById('move-z-10mm');
const moveZ100mmButton = document.getElementById('move-z-100mm');

// Сначала получите элемент статуса
const printStatus = document.getElementById('print-status');

// Функция для изменения статуса
function changeStatus(newStatus) {
    printStatus.textContent = "Status: " + newStatus;
}

// Функции для управления движением по осям
function moveAxis(axis, distance) {
    // Здесь можно добавить логику для перемещения по указанной оси на указанное расстояние
    console.log(`Moved ${distance}mm along axis ${axis}`);
}


moveX-10mmButton.addEventListener('click', function () {
    changeStatus('Moving X axis by -10mm');
    moveAxis('X', -10); // Перемещение по оси X на -10 мм
});

moveX100mmButton.addEventListener('click', function () {
    changeStatus('Moving X axis by -100mm');
    moveAxis('X', -100); // Перемещение по оси X на -100 мм
});
moveX+10mmButton.addEventListener('click', function () {
    changeStatus('Moving X axis by 10mm');
    moveAxis('X', 10); // Перемещение по оси X на 10 мм
});

moveX100mmButton.addEventListener('click', function () {
    changeStatus('Moving X axis by 100mm');
    moveAxis('X', 100); // Перемещение по оси X на 100 мм
});

moveY10mmButton.addEventListener('click', function () {
    changeStatus('Moving Y axis by 10mm');
    moveAxis('Y', 10); // Перемещение по оси Y на 10 мм
});

moveY100mmButton.addEventListener('click', function () {
    changeStatus('Moving Y axis by 100mm');
    moveAxis('Y', 100); // Перемещение по оси Y на 100 мм
});

moveZ10mmButton.addEventListener('click', function () {
    changeStatus('Moving Z axis by 10mm');
    moveAxis('Z', 10); // Перемещение по оси Z на 10 мм
});

moveZ100mmButton.addEventListener('click', function () {
    changeStatus('Moving Z axis by 100mm');
    moveAxis('Z', 100); // Перемещение по оси Z на 100 мм
});
