Документация по админке проекта

---

## 1. Общая идея структуры админки

Вместо одного огромного `admin.py` админка разбита на пакет `admin/` с тематическими модулями.

Структура:

```text
main/
  admin/
    __init__.py
    inlines.py
    university.py
    people.py
    learning.py
    requests_admin.py
    applicant.py
    news.py
    schedule_admin.py
    notifications.py
````

## 2. `admin/__init__.py` - точка входа админки

**Назначение:**

* настроить заголовки админки
* "подтянуть" все остальные модули, чтобы сработали `@admin.register(...)`.

Основные действия:

* Настраиваются заголовки админ-панели:

  * `site_header` - текст в шапке админки
  * `site_title` - заголовок страницы браузера
  * `index_title` - заголовок главной страницы админки

* Импортируются все остальные файлы админки:

  ```python
  from .university import *
  from .people import *
  from .learning import *
  from .requests_admin import *
  from .applicant import *
  from .news import *
  from .schedule_admin import *
  from .notifications import *
  ```

Важно:

* явный импорт нужен, чтобы декораторы `@admin.register(Model)` реально выполнялись.
* отдельный файл `inlines.py` тоже импортируется, но он сам по себе не регистрирует модели, просто содержит inline классы.

---

## 3. `admin/inlines.py` - общие инлайны

**Назначение:**
Собраны все `Inline` классы, которые используются в других админ файлах. Это уменьшает дублирование и разводит ответственность.

Инлайны:

* `StudentRoleInline`

  * Инлайн для ролей студента (староста, журналист и т.п.).
  * Используется внутри `StudentAdmin`.
  * Показывает поля:

    * role
    * start_date
    * end_date

* `EnrollmentInline`

  * Инлайн для связки студент - курс (Enrollment).
  * Используется в `StudentAdmin` и `TeachingAdmin`.
  * Поля:

    * student
    * teaching
    * is_active
    * date_enrolled (только чтение).

* `AssessmentInline`

  * Инлайн для элементов оценивания на курсе (ДЗ, тесты, экзамены).
  * Используется в `TeachingAdmin`.
  * Поля:

    * title
    * type
    * max_points
    * weight
    * due_at
    * is_final

* `AssessmentResultInline`

  * Инлайн для результатов по конкретной работе.
  * Используется в `AssessmentAdmin`.
  * Поля:

    * student
    * attempt
    * points
    * graded_at (readonly)
    * grade_5
    * grade_ects

* `ApplicantExamInline`

  * Инлайн таблица для экзаменов абитуриента.
  * Можно видеть сразу все ЕГЭ/вступительные у одного Applicant.

* `TeachingInline`

  * Инлайн с курсами, которые ведет преподаватель.
  * Используется в `TeacherAdmin`.
  * Поля:

    * curriculum
    * group
    * academic_year
    * semester_in_year

* `ScheduleExceptionInline`

  * Инлайн для исключений расписания внутри `ScheduleSlotAdmin`.
  * Поля:

    * date
    * action
    * новые параметры (new_date, new_start_time и т.д.)
    * created_at (readonly)
  * Сворачивается (`classes = ("collapse",)`) чтобы не загромождать форму.

---

## 4. `admin/university.py` - структуры университета

**Модели:**

* `University`
* `Faculty`
* `Program`
* `Discipline`
* `Curriculum`

### UniversityAdmin

Отвечает за список вузов.

* `list_display`:

  * short_name
  * name
  * city
  * contact_email

* Есть поиск по названию, короткому названию и городу.

### FacultyAdmin

Факультеты.

* `list_display`:

  * name
  * university

* `list_filter` по университету

* `autocomplete_fields = ("university",)` - удобно выбирать университет из большого списка.

### ProgramAdmin

Образовательные программы.

* `list_display`:

  * name
  * code
  * faculty
  * duration_years

* Фильтрация по:

  * `faculty__university`
  * `faculty`

* Поиск:

  * по имени программы
  * коду
  * названию факультета
  * названию университета

### DisciplineAdmin

Дисциплины (ООП, матан и т.п.)

* `list_display`:

  * title
  * code
  * ects

* Поиск по:

  * title
  * code

### CurriculumAdmin

Учебные планы - какая дисциплина в каком семестре и с какими параметрами.

* `list_display`:

  * program
  * discipline
  * semester
  * hours
  * control_form

* Фильтры:

  * `program__faculty__university`
  * `program__faculty`
  * `program`
  * `semester`
  * `control_form`

* `autocomplete_fields = ("program", "discipline")` - удобно не таскать огромные списки.

---

## 5. `admin/people.py` - роли, люди, преподаватели, группы, студенты

**Модели:**

* `Role`
* `Person`
* `Teacher`
* `StudentGroup`
* `Student`

Плюс инлайны:

* `StudentRoleInline`
* `EnrollmentInline`
* `TeachingInline`

### RoleAdmin

* Показывает название роли и ее permission-код.
* Можно фильтровать по типу permission.

### PersonAdmin

Базовая сущность человека.

* `list_display`:

  * ФИО
  * email
  * phone
  * vk_user_id
  * role

* Фильтрация:

  * по `role__permission`

* `autocomplete_fields = ("user", "role")`

  * связка с Django User
  * выбор роли.

### TeacherAdmin

Преподаватели.

* `list_display`:

  * person
  * department
  * academic_title
  * university

* Фильтры:

  * по университету
  * по кафедре (department)

* Поиск по фамилии, имени, кафедре.

* `inlines = [TeachingInline]`

  * из карточки преподавателя можно сразу смотреть/редактировать курсы, которые он ведет.

### StudentGroupAdmin

Студенческие группы (ПО-51 и т.п.)

* `list_display`:

  * name
  * program
  * admission_year
  * university
  * curator

* Фильтры:

  * по university
  * по факультету через `program__faculty`
  * по программе
  * по году набора

* Поиск:

  * по названию группы
  * названию программы
  * имени факультета
  * названию университета
  * фамилии куратора

### StudentAdmin

Студенты.

* `list_display`:

  * person
  * student_id
  * student_group
  * university
  * current_year
  * admission_year

* Фильтры:

  * по университету
  * по факультету через группу
  * по группе
  * по курсу (current_year)
  * по году поступления

* `inlines = [StudentRoleInline, EnrollmentInline]`

  * можно сразу видеть:

    * роли студента (например староста)
    * записи о зачислении на курсы.

---

## 6. `admin/learning.py` - учебный процесс

**Модели:**

* `Teaching`
* `Enrollment`
* `Assessment`
* `AssessmentResult`

### TeachingAdmin

Курс - конкретное чтение дисциплины (Teacher + Curriculum + Group + год + семестр).

* `list_display`:

  * teacher
  * curriculum
  * group
  * academic_year
  * semester_in_year

* Фильтры:

  * университет преподавателя
  * учебный год
  * семестр
  * группа
  * программа (через curriculum)

* Использует инлайны:

  * `AssessmentInline`
  * `EnrollmentInline`

То есть из админки курса можно:

* увидеть все элементы оценивания
* увидеть всех зачисленных студентов (Enrollment).

### EnrollmentAdmin

Связь студент - курс.

* `list_display`:

  * student
  * teaching
  * is_active
  * date_enrolled

* Фильтры:

  * активен или нет
  * год и семестр курса
  * университет преподавателя

* `date_hierarchy = "date_enrolled"`

  * можно легко фильтровать по дате зачисления.

### AssessmentAdmin

Элементы оценивания (дз, тесты и т.д.)

* `list_display`:

  * title
  * teaching
  * type
  * max_points
  * weight
  * due_at
  * is_final

* Фильтры:

  * по типу (hw, quiz и т.п.)
  * по is_final
  * по году и семестру курса

* `inlines = [AssessmentResultInline]`

  * сразу из работы видно все результаты студентов.

### AssessmentResultAdmin

Результаты по конкретным работам.

* `list_display`:

  * assessment
  * student
  * attempt
  * points
  * grade_5
  * grade_ects
  * graded_at

* Фильтры:

  * тип работы
  * оценка по пятибалльной шкале
  * оценка в ECTS
  * дата выставления

* Только чтение для `graded_at`.

---

## 7. `admin/requests_admin.py` - внутренние заявления

**Модели:**

* `StudentRequest`
* `TeacherRequest`

### StudentRequestAdmin

Заявления от студентов (справки, общежитие и т.п.)

* `list_display`:

  * student
  * university
  * type
  * status
  * created_at
  * updated_at

* Фильтры по:

  * университету
  * типу
  * статусу
  * дате создания

* `readonly_fields`:

  * created_at
  * updated_at

### TeacherRequestAdmin

Заявления от преподавателей (отпуск, больничный и т.п.)

* Почти аналогично StudentRequestAdmin:

  * teacher
  * university
  * type
  * status
  * created_at / updated_at
  * фильтры и поиск по фамилии преподавателя и кафедре.

---

## 8. `admin/applicant.py` - абитуриенты и их заявки

**Модели:**

* `Applicant`
* `ApplicantExam`
* `AdmissionRequest`
* `ApplicationRequest`

### ApplicantAdmin

Абитуриенты.

* `list_display`:

  * person
  * birth_date
  * school_name
  * graduation_year
  * linked_student

* Можно искать по фамилии, имени, школе, номеру паспорта.

### ApplicantExamAdmin

Экзамены абитуриента (ЕГЭ и т.п.)

* `list_display`:

  * applicant
  * subject
  * exam_type
  * score

* `list_filter` по типу экзамена.

### AdmissionRequestAdmin

Заявки абитуриентов на программу.

* `list_display`:

  * ФИО
  * email
  * desired_program
  * study_form
  * status
  * created_at

* Фильтры:

  * по форме обучения
  * по статусу
  * по дате создания

### ApplicationRequestAdmin

Отдельная модель заявления на поступление (из формы на сайте).

* Аналогичная админка:

  * поля личных данных
  * информация о поступлении
  * системная информация (status, created_at)
  * разбито по `fieldsets` для удобства.

---

## 9. `admin/news.py` - новости

**Модель:**

* `NewsPost`

Фишки:

* `list_display`:

  * title
  * news_icon
  * university
  * is_published
  * published_at
  * author
  * cover_thumb (миниатюра)

* `cover_thumb` рисует превью обложки в таблице через `format_html`.

* `date_hierarchy = "published_at"`

  * можно по датам быстро ходить.

Экшены:

* `publish_now`

  * проставляет `is_published = True` и `published_at = timezone.now()` для выбранных записей.

* `unpublish`

  * снимает с публикации (is_published = False).

---

## 10. `admin/schedule_admin.py` - расписание и исключения

**Модели:**

* `ScheduleSlot`
* `ScheduleException`

### ScheduleSlotAdmin

Ячейка расписания - повторяющаяся пара.

* `inlines = [ScheduleExceptionInline]`

  * можно прямо из ячейки добавлять исключения.

* `list_display`:

  * id
  * university
  * get_discipline
  * get_teacher
  * weekday
  * start_time
  * end_time
  * week_parity
  * date_range
  * rooms
  * groups_count

* Вспомогательные методы:

  * `get_discipline` - название дисциплины
  * `get_teacher` - ФИО преподавателя
  * `date_range` - период действия слота
  * `rooms` - текстовое представление корпуса и аудитории
  * `groups_count` - сколько групп привязано.

* Фильтры:

  * по университету
  * по дню недели
  * по четности недели
  * по группам
  * по преподавателю

* `filter_horizontal = ("groups",)`

  * удобный виджет для выбора нескольких групп.

### ScheduleExceptionAdmin

Исключения расписания (отмена, перенос, смена аудитории).

* `list_display`:

  * id
  * date
  * action
  * slot
  * slot_university
  * slot_weekday
  * slot_time
  * slot_discipline
  * slot_teacher

* Методы `slot_*` вытаскивают полезную информацию из связанного `ScheduleSlot`.

* Фильтры:

  * по action (cancel, move, change_room)
  * по дате
  * по университету
  * по дню недели.

---

## 11. `admin/notifications.py` - групповые оповещения

**Модель:**

* `GroupNotification`

Дополнительно используется `GroupNotificationForm` для валидации.

Форма:

* проверяет, что:

  * `group.university_id == university.id`
* если нет - добавляет ошибку на поле `group`.

Админка:

* `list_display`:

  * icon_display
  * short_text
  * group
  * university
  * sender
  * created_at

* `icon_display` - красиво показывает эмодзи иконки.

* `short_text` - обрезает текст до 80 символов, чтобы список был читабельным.

* `list_filter`:

  * по университету
  * по группе
  * по программе группы
  * по дате создания

* `autocomplete_fields`:

  * university
  * group
  * sender

* `readonly_fields`:

  * created_at

* `date_hierarchy = "created_at"`

---

## 12. Как расширять админку дальше

Если нужно добавить новую модель в админку:

1. Добавить модель в `models/`
2. Выбрать подходящий модуль в `admin/`:
3. Добавить туда `@admin.register(НоваяМодель)` и описать `ModelAdmin`.
4. Ничего больше менять не нужно - `__init__.py` уже импортирует все подмодули.

