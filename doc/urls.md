## Документация по маршрутам приложения

---

# 📁 Структура пакета `urls`

```
main/
  urls/
    __init__.py
    public.py
    news.py
    student.py
    teacher.py
    moderation.py
    applicant.py
```

Каждый файл отвечает за свой функциональный блок, а `__init__.py` собирает всё в единый `urlpatterns`.

---

# 🧩 1. `urls/__init__.py`

Главный файл, который объединяет маршруты всех подпакетов в один список.

```python
urlpatterns = []
urlpatterns += public_patterns
urlpatterns += news_patterns
urlpatterns += student_patterns
urlpatterns += teacher_patterns
urlpatterns += moderation_patterns
urlpatterns += applicant_patterns
```

Если нужно отключить целый слой (например, applicant), достаточно закомментировать одну строку.

---

# 🌐 2. `urls/public.py`

| Путь        | Имя            | Описание                          |
| ----------- | -------------- | --------------------------------- |
| `/`         | `index`        | Главная страница                  |
| `/profile/` | `profile_view` | Просмотр и редактирование профиля |
| `/help/`    | `help_page`    | Центр помощи                      |


---

# 📰 3. `urls/news.py`

Работа с новостями и их модерацией.

| Путь                                        | Имя                     | Описание                    |
| ------------------------------------------- | ----------------------- | --------------------------- |
| `/news/`                                    | `news_view`             | Лента новостей              |
| `/news/<int:news_id>/`                      | `news_detail`           | Просмотр одной новости      |
| `/news/<slug:news_slug>/`                   | `news_moderation`       | Модерация общей новости     |
| `/news/<slug:group_slug>/<slug:news_slug>/` | `group_news_moderation` | Модерация групповой новости |


---

# 🎓 4. `urls/student.py`

Маршруты для студентов, старост, журналистов.

| Путь                | Имя                       | Описание                      |
| ------------------- | ------------------------- | ----------------------------- |
| `/schedule/`        | `student_schedule_view`   | Расписание студента           |
| `/grades/`          | `student_grades_view`     | Оценки                        |
| `/group/`           | `student_group_view`      | Информация о группе           |
| `/student_request/` | `student_request_view`    | Подача заявлений              |
| `/group_news/`      | `headman_group_news_view` | Новости группы (староста)     |
| `/create_news/`     | `journalist_news_view`    | Создание новостей (журналист) |


---

# 👨‍🏫 5. `urls/teacher.py`

Маршруты для преподавателей.

| Путь                   | Имя                        | Описание                 |
| ---------------------- | -------------------------- | ------------------------ |
| `/teacher_schedule/`   | `teacher_schedule_view`    | Расписание преподавателя |
| `/teacher_subjects/`   | `teacher_subjects_view`    | Предметы                 |
| `/teacher_workingoff/` | `teacher_working_off_view` | Отработка занятий        |
| `/teacher_request/`    | `teacher_request_form`     | Заявки преподавателя     |
| `/teacher_make_alert/` | `teacher_make_alert_form`  | Уведомления группе       |

---

# 🛠 6. `urls/moderation.py`


### 🔷 Общая модерация

| Путь                      | Имя                     |
| ------------------------- | ----------------------- |
| `/moderation_staff/`      | `moderation_staff`      |
| `/moderation_university/` | `moderation_university` |
| `/student_list/`          | `student_admin_list`    |

### 🔷 Расписание

| Путь                                  | Имя                         |
| ------------------------------------- | --------------------------- |
| `/moderation_schedule/`               | `moderation_schedules`      |
| `/moderation_schedule/slot/new/`      | `schedule_slot_create`      |
| `/moderation_schedule/exception/new/` | `schedule_exception_create` |

### 🔷 Учебный контент (subject management)

| Путь                   | Имя                   |
| ---------------------- | --------------------- |
| `/moderation_subject/` | `moderation_subjects` |

#### Дисциплины

| Путь                                               | Имя                 |
| -------------------------------------------------- | ------------------- |
| `/moderation_subject/disciplines/`                 | `disciplines_list`  |
| `/moderation_subject/disciplines/<int:pk>/edit/`   | `discipline_edit`   |
| `/moderation_subject/disciplines/<int:pk>/delete/` | `discipline_delete` |

#### Учебный план (Curriculum)

| Путь                                              | Имя                 |
| ------------------------------------------------- | ------------------- |
| `/moderation_subject/curriculum/`                 | `curriculum_list`   |
| `/moderation_subject/curriculum/<int:pk>/edit/`   | `curriculum_edit`   |
| `/moderation_subject/curriculum/<int:pk>/delete/` | `curriculum_delete` |

#### Teaching

| Путь                                            | Имя               |
| ----------------------------------------------- | ----------------- |
| `/moderation_subject/teaching/`                 | `teaching_list`   |
| `/moderation_subject/teaching/<int:pk>/edit/`   | `teaching_edit`   |
| `/moderation_subject/teaching/<int:pk>/delete/` | `teaching_delete` |

### 🔷 Заявления и акты

| Путь                    | Имя                   |
| ----------------------- | --------------------- |
| `/moderation_requests/` | `moderation_requests` |
| `/moderation_acts/`     | `moderation_acts`     |

---

# 📝 7. `urls/applicant.py`

Маршруты для абитуриентов.

| Путь                  | Имя                      | Описание                 |
| --------------------- | ------------------------ | ------------------------ |
| `/admission_request/` | `admission_request_page` | Заявление на поступление |
| `/applicant_chat/`    | `applicant_chat`         | Чат с приёмной комиссией |
| `/applicant_rating/`  | `applicant_rating`       | Рейтинг абитуриентов     |


---

