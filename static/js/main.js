document.addEventListener('DOMContentLoaded', () => {
    const flaskData = document.getElementById('flask-data');
    const editPassword = flaskData ? flaskData.dataset.editPassword : null;
    const saveUrl = flaskData ? flaskData.dataset.saveUrl : null;
    const scheduleUrl = flaskData ? flaskData.dataset.scheduleUrl : null;
    const totalWeeks = 19;
    let currentWeek = 1;
    let scheduleData = {};
    let isEditMode = false;
    
    // Отладочная информация
    let debugInfo = {
        messages: [],
        addMessage: function(msg) {
            const timestamp = new Date().toLocaleTimeString();
            this.messages.push(`[${timestamp}] ${msg}`);
            console.log(msg);
            this.updateDisplay();
        },
        updateDisplay: function() {
            const debugContent = document.getElementById('debug-content');
            if (debugContent) {
                debugContent.innerHTML = this.messages.join('<br>');
            }
        }
    };
    
    // Добавляем базовую информацию
    debugInfo.addMessage(`Vercel Preview Debug Info:`);
    debugInfo.addMessage(`editPassword set: ${editPassword ? 'Yes' : 'No'}`);
    debugInfo.addMessage(`saveUrl: ${saveUrl || 'Not Set'}`);
    debugInfo.addMessage(`scheduleUrl: ${scheduleUrl || 'Not Set'}`);
    
    function updateProgressBar() {
        const progressFill = document.getElementById("progress-fill");
        const progressText = document.getElementById("progress-text");

        // Проверяем, что currentWeek не превышает totalWeeks
        const safeCurrentWeek = Math.min(Math.max(currentWeek, 1), totalWeeks);
        
        const progressPercentage = ((safeCurrentWeek - 1) / (totalWeeks - 1)) * 100;
        
        if (progressFill) {
            progressFill.style.width = `${progressPercentage}%`;
            console.log("Progress width:", `${progressPercentage}%`); // Для отладки
        }

        if (progressText) {
            progressText.textContent = `Прогресс: ${progressPercentage.toFixed(1)}%`;
        }
    }

    // Удаляем внутренний обработчик DOMContentLoaded
    updateProgressBar();

    const weekMapping = [
    { week: 1, start: "2025-02-08", end: "2025-02-17" },
    { week: 2, start: "2025-02-17", end: "2025-02-22" },
    { week: 3, start: "2025-02-23", end: "2025-02-29" },
    { week: 4, start: "2025-03-29", end: "2025-03-08" },
    { week: 5, start: "2025-03-09", end: "2025-03-15" },
    { week: 6, start: "2025-03-15", end: "2025-03-22" },
    { week: 7, start: "2025-03-23", end: "2025-03-29" },
    { week: 8, start: "2025-03-28", end: "2025-04-05" },
    { week: 9, start: "2025-04-06", end: "2025-04-12" },
    { week: 10, start: "2025-04-13", end: "2025-04-19" },
    { week: 11, start: "2025-04-20", end: "2025-04-26" },
    { week: 12, start: "2025-04-27", end: "2025-05-03" },
    { week: 13, start: "2025-05-04", end: "2025-05-10" },
    { week: 14, start: "2025-05-11", end: "2025-05-17" },
    { week: 15, start: "2025-05-18", end: "2025-05-24" },
    { week: 16, start: "2025-05-25", end: "2025-05-31" },
    { week: 17, start: "2025-06-01", end: "2025-06-07" },
    { week: 18, start: "2025-06-08", end: "2025-06-14" },
    { week: 19, start: "2025-06-15", end: "2025-06-21" }
];

function getCurrentWeek() {
    const today = new Date();
    for (const period of weekMapping) {
        const startDate = new Date(period.start);
        const endDate = new Date(period.end);
        if (today >= startDate && today <= endDate) {
            return period.week;
        }
    }
    console.log("Не удалось определить текущую неделю, используем неделю 1");
    return 1; // Default to week 1 if no match
}

// Устанавливаем текущую неделю при загрузке
currentWeek = getCurrentWeek();
console.log("Установлена текущая неделя:", currentWeek);

    async function loadSchedule() {
      try {
        debugInfo.addMessage(`Загрузка расписания из: ${scheduleUrl}`);
        
        if (!scheduleUrl) {
          const error = 'scheduleUrl не определен или пуст';
          debugInfo.addMessage(`Ошибка: ${error}`);
          throw new Error('URL для загрузки расписания не настроен');
        }
        
        // Добавляем случайный параметр к URL, чтобы избежать кэширования
        const urlWithCache = `${scheduleUrl}?_=${new Date().getTime()}`;
        debugInfo.addMessage(`URL с параметром против кэширования: ${urlWithCache}`);
        
        debugInfo.addMessage('Отправка запроса...');
        const response = await fetch(urlWithCache, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });
        debugInfo.addMessage(`Статус ответа: ${response.status} ${response.statusText}`);
        
        if (!response.ok) {
          const error = `HTTP ошибка: ${response.status} ${response.statusText}`;
          debugInfo.addMessage(error);
          throw new Error(`Ошибка HTTP! Статус: ${response.status}`);
        }
        
        const responseText = await response.text();
        debugInfo.addMessage(`Длина текста ответа: ${responseText.length} символов`);
        
        if (responseText.length < 100) {
          debugInfo.addMessage(`Предпросмотр ответа: ${responseText}`);
        } else {
          debugInfo.addMessage(`Предпросмотр ответа: ${responseText.substring(0, 100)}...`);
        }
        
        if (!responseText || responseText.trim() === '') {
          debugInfo.addMessage('Получен пустой ответ');
          throw new Error('Получен пустой ответ от сервера');
        }
        
        try {
          debugInfo.addMessage('Попытка разобрать JSON...');
          scheduleData = JSON.parse(responseText);
          debugInfo.addMessage('JSON успешно разобран');
        } catch (parseError) {
          debugInfo.addMessage(`Ошибка при разборе JSON: ${parseError.message}`);
          throw new Error('Ошибка при обработке данных расписания');
        }
        
        const weeks = Object.keys(scheduleData);
        debugInfo.addMessage(`Данные расписания содержат недели: ${weeks.join(', ')}`);
        
        if (weeks.length === 0) {
          debugInfo.addMessage('Расписание пусто или не содержит данных');
          const table = document.getElementById("schedule-table");
          table.innerHTML = "<tr><td>Расписание пока не заполнено</td></tr>";
          return;
        }
        
        // If the current week doesn't exist in the data, default to week 1
        if (!scheduleData[currentWeek]) {
          debugInfo.addMessage(`Нет данных для недели ${currentWeek}, переключаемся на неделю 1`);
          currentWeek = 1;
        }
        
        renderTable(currentWeek);
      } catch (error) {
        debugInfo.addMessage(`Критическая ошибка: ${error.message}`);
        const table = document.getElementById("schedule-table");
        table.innerHTML = `<tr><td>Ошибка загрузки данных: ${error.message}</td></tr>`;
      }
    }

    function renderTable(week) {
      const table = document.getElementById("schedule-table");
      table.innerHTML = ""; // Очищаем таблицу

      // Make sure we're using a string key for the week
      const weekKey = week.toString();

      if (!scheduleData || !scheduleData[weekKey]) {
        debugInfo.addMessage(`Данные для недели ${weekKey} не найдены`);
        
        if (Object.keys(scheduleData).length > 0) {
          // Если есть другие недели, используем первую доступную
          const availableWeeks = Object.keys(scheduleData);
          debugInfo.addMessage(`Доступные недели: ${availableWeeks.join(', ')}`);
          
          if (availableWeeks.length > 0) {
            const firstWeek = availableWeeks[0];
            debugInfo.addMessage(`Переключаемся на неделю ${firstWeek}`);
            currentWeek = parseInt(firstWeek);
            renderTable(currentWeek);
            return;
          }
        }
        
        table.innerHTML = "<tr><td>Нет данных для этой недели</td></tr>";
        return;
      }
      
      debugInfo.addMessage(`Рендеринг данных для недели ${weekKey}`);
      
      // Создаем тело таблицы
      const tbody = document.createElement("tbody");
      table.appendChild(tbody);

      const daysOrder = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
      
      daysOrder.forEach(day => {
        if (!scheduleData[weekKey][day]) {
          debugInfo.addMessage(`Нет данных для дня ${day} в неделе ${weekKey}`);
          return;
        }

        // Заголовок дня
        const dayRow = document.createElement("tr");
        const dayCell = document.createElement("td");
        dayCell.classList.add("day-header");
        dayCell.colSpan = "2";
        dayCell.textContent = day;
        dayRow.appendChild(dayCell);
        tbody.appendChild(dayRow);

        // Уроки дня
        scheduleData[weekKey][day].forEach((lessonText, index) => {
          const parts = lessonText.split(" | ");
          const time = parts[0] || "";
          const subject = parts.length > 1 ? parts[1] : "";
          
          const lessonRow = document.createElement("tr");
          
          const timeCell = document.createElement("td");
          timeCell.classList.add("lesson-time");
          timeCell.textContent = time;
          
          const subjectCell = document.createElement("td");
          subjectCell.classList.add("lesson-subject");
          subjectCell.contentEditable = isEditMode;
          subjectCell.textContent = subject || "";

          if (isEditMode) {
            subjectCell.style.backgroundColor = "#fff3cd";
            subjectCell.addEventListener("input", (e) => {
              scheduleData[weekKey][day][index] = `${time} | ${e.target.textContent}`;
            });
          }

          lessonRow.appendChild(timeCell);
          lessonRow.appendChild(subjectCell);
          tbody.appendChild(lessonRow);
        });
      });

      // Обновление отображения текущей недели
      document.getElementById("currentWeekDisplay").textContent = `Неделя ${week}`;
      document.getElementById("prevWeek").disabled = (week === 1);
      document.getElementById("nextWeek").disabled = (week === totalWeeks);
      
      updateProgressBar(); 
    }

    document.getElementById("prevWeek").addEventListener("click", () => {
      if (currentWeek > 1) {
        currentWeek--;
        renderTable(currentWeek);
        updateProgressBar();
      }
    });

    document.getElementById("nextWeek").addEventListener("click", () => {
      if (currentWeek < totalWeeks) {
        currentWeek++;
        renderTable(currentWeek);
        updateProgressBar();
      }
    });

    // Добавляем обработчик для кнопки логина
    document.getElementById("loginBtn").addEventListener("click", async function() {
      console.log('Текущий режим редактирования:', isEditMode);
      
      if (!isEditMode) {
        const password = prompt("Введите пароль для редактирования:");
        console.log('Введенный пароль:', password);
        
        // Send the password to the server for verification
        const response = await fetch('/api/verify-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        const result = await response.json();
        if (result.success) {
            console.log('Пароль верный!');
            isEditMode = true;
            this.textContent = "Выйти";
            document.getElementById("editNotice").style.display = "block";
            document.getElementById("saveBtn").style.display = "block";
            renderTable(currentWeek);
        } else {
            alert("Неверный пароль!");
        }
      } else {
        isEditMode = false;
        this.textContent = "Логин";
        document.getElementById("editNotice").style.display = "none";
        document.getElementById("saveBtn").style.display = "none";
        renderTable(currentWeek);
      }
    });

    document.getElementById("saveBtn").addEventListener("click", async function () {
      try {
        // Send the schedule data to the server with password authentication
        const response = await fetch(saveUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            password: editPassword,
            schedule: scheduleData
          }),
        });

        const result = await response.json();
        if (result.error) {
          throw new Error(result.error);
        }

        alert("Расписание успешно сохранено!");
      } catch (error) {
        console.error("Ошибка:", error);
        alert("Ошибка при сохранении: " + error.message);
      }
    });
       
    loadSchedule();
});
