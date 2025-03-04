document.addEventListener('DOMContentLoaded', () => {
    const flaskData = document.getElementById('flask-data');
    const editPassword = flaskData.dataset.editPassword;
    const saveUrl = flaskData.dataset.saveUrl;
    const scheduleUrl = flaskData.dataset.scheduleUrl;
    const totalWeeks = 19;
    let currentWeek = 1;
    let scheduleData = {};
    let isEditMode = false;
    const EDIT_PASSWORD = flaskData.dataset.editPassword;

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

    document.addEventListener('DOMContentLoaded', () => {
        updateProgressBar();
    });

    const weekMapping = [
    { week: 1, start: "2025-02-08", end: "2025-02-17" },
    { week: 2, start: "2025-02-17", end: "2025-02-22" },
    { week: 3, start: "2025-02-23", end: "2025-02-29" },
    { week: 4, start: "2025-03-01", end: "2025-03-08" },
    { week: 5, start: "2025-03-09", end: "2025-03-15" },
    { week: 6, start: "2025-03-16", end: "2025-03-22" },
    { week: 7, start: "2025-03-23", end: "2025-03-29" },
    { week: 8, start: "2025-03-30", end: "2025-04-05" },
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
    return 1;
}

// Определение четности/нечетности недели
function getParityWeek(weekNumber) {
    // Если неделя четная, возвращаем "2" (четная), иначе "1" (нечетная)
    return weekNumber % 2 === 0 ? "2" : "1";
}

// Устанавливаем текущую неделю при загрузке
currentWeek = getCurrentWeek();

    async function loadSchedule() {
      try {
        const response = await fetch(scheduleUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        scheduleData = await response.json();
        console.log('Загруженные данные:', scheduleData); 
        
        renderTable(currentWeek);
      } catch (error) {
        console.error("Ошибка загрузки расписания:", error);
        const table = document.getElementById("schedule-table");
        table.innerHTML = "<tr><td>Ошибка загрузки данных</td></tr>";
      }
    }

    function renderTable(week) {
      const table = document.getElementById("schedule-table");
      table.innerHTML = ""; // Очищаем таблицу
      
      // Определяем четность/нечетность недели для выбора расписания
      const parityWeek = getParityWeek(week);
      console.log(`Неделя ${week}, Четность: ${parityWeek === "2" ? "четная" : "нечетная"}`);

      if (!scheduleData || !scheduleData[parityWeek]) {
        table.innerHTML = "<tr><td>Нет данных для этой недели</td></tr>";
        console.error('Данные для недели c четностью', parityWeek, 'не найдены');
        return;
      }
      // Создаем тело таблицы
      const tbody = document.createElement("tbody");
      table.appendChild(tbody);

      const daysOrder = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
      
      daysOrder.forEach(day => {
        if (!scheduleData[parityWeek][day]) return;

        // Заголовок дня
        const dayRow = document.createElement("tr");
        const dayCell = document.createElement("td");
        dayCell.classList.add("day-header");
        dayCell.colSpan = "2";
        dayCell.textContent = day;
        dayRow.appendChild(dayCell);
        tbody.appendChild(dayRow);

        // Уроки дня
        scheduleData[parityWeek][day].forEach((lessonText, index) => {
          const [time, subject] = lessonText.split(" | ");
          
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
              scheduleData[parityWeek][day][index] = `${time} | ${e.target.textContent}`;
            });
          }

          lessonRow.appendChild(timeCell);
          lessonRow.appendChild(subjectCell);
          tbody.appendChild(lessonRow);
        });
      });

      // Обновление отображения текущей недели и добавление информации о четности
      const parityText = parityWeek === "2" ? "четная" : "нечетная";
      document.getElementById("currentWeekDisplay").textContent = `Неделя ${week} (${parityText})`;
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
    document.getElementById("loginBtn").addEventListener("click", function() {
      console.log('Текущий режим редактирования:', isEditMode);
      
      if (!isEditMode) {
        const password = prompt("Введите пароль для редактирования:");
        console.log('Введенный пароль:', password);
        
        if (password === EDIT_PASSWORD) {
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

    // Добавляем обработчик сохранения
    document.getElementById("saveBtn").addEventListener("click", async function() {
      try {
        const response = await fetch(saveUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            password: EDIT_PASSWORD,
            schedule: scheduleData
          }),
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success) {
            alert("Изменения успешно сохранены!");
          } else {
            alert(`Ошибка при сохранении: ${result.error || "неизвестная ошибка"}`);
          }
        } else {
          alert("Ошибка при сохранении!");
        }
      } catch (error) {
        console.error("Ошибка:", error);
        alert("Сервер недоступен!");
      }
    });

    // Добавить проверку полученного пароля
    console.log('Пароль из Flask:', EDIT_PASSWORD);
   
    loadSchedule();
});
