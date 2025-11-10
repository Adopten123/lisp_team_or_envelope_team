
# Цифровой вуз — документация к `models.py` (подробно)

> База: **Django ORM**, СУБД: **SQLite** (совместимо с Postgres/MySQL)  
> Назначение: мультивузовый сервис (одна инсталляция — несколько университетов).  
> Версия файла: **1.1**

---

## Содержание

- [Обзор архитектуры](#обзор-архитектуры)
- [Диаграмма связей (укороченно)](#диаграмма-связей-укороченно)
- [Модели и поля](#модели-и-поля)
  - [Person](#person)
  - [Teacher](#teacher)
  - [StudentGroup](#studentgroup)
  - [Student](#student)
  - [University](#university)
  - [Faculty](#faculty)
  - [Program](#program)
  - [Discipline](#discipline)
  - [Curriculum](#curriculum)
  - [Teaching](#teaching)
  - [StudentRole](#studentrole)
  - [Enrollment](#enrollment)
  - [Assessment](#assessment)
  - [AssessmentResult](#assessmentresult)
  - [StudentRequest](#studentrequest)
  - [TeacherRequest](#teacherrequest)
  - [Applicant](#applicant)
  - [ApplicantExam](#applicantexam)
  - [AdmissionRequest](#admissionrequest)
- [Индексы и уникальные ограничения](#индексы-и-уникальные-ограничения)
- [Типовые запросы (QuerySet)](#типовые-запросы-queryset)
- [Валидация и бизнес-правила](#валидация-и-бизнес-правила)
- [Рекомендации по админке](#рекомендации-по-админке)
- [Переносимость и миграции](#переносимость-и-миграции)
- [Дорожная карта расширений](#дорожная-карта-расширений)

---

## Обзор архитектуры

Схема определяет **базовый класс** (`Person`) и **его наследников (роли)** (`Student`, `Teacher`, `Applicant`).  
Иерархия структур внутри университета: `University → Faculty → Program → StudentGroup`.  
Учебный план (`Curriculum`) и класс текущей учебной дисциплины (`Teaching`) описывают,
кто и в какой год/семестр ведёт дисциплину в конкретной группе.  
Система оценивания состоит из **элементов контроля** (`Assessment`) и **результатов** (`AssessmentResult`) в разрезе **зачислений** (`Enrollment`).  
Заявления унифицированы: `StudentRequest`, `TeacherRequest`. 
Абитуриенты: `Applicant`, результаты экзаменов `ApplicantExam` и заявки `AdmissionRequest`.

`University` — большинство сущностей прямо или косвенно связаны с конкретным вузом.

---

## Диаграмма связей 

```
Person ─┬─1:1─> Student ───────────────┐
        ├─1:1─> Teacher ──┐            │
        └─1:1─> Applicant │            │
                          │            │
University ──┬─> Faculty ──┬─> Program ──┬─> StudentGroup ──┬─> StudentRole
             │             │             └─> Teaching <─────┘
             │             └─> Curriculum <─────────────────┘
             │                                   │
             ├─> teachers/students/requests      └─> Enrollment ──┬─> Assessment ──┬─> AssessmentResult
             └─> (через related_name)                               (в рамках Teaching)
```

---

## Модели и поля

### `Person`
**Назначение:** базовый объект человека (ФИО, контакты, VK/Max ID) и связка с `auth.User`.

| Поле | Тип | Обяз. | Описание |
|---|---|:--:|---|
| `user` | OneToOne → `AUTH_USER_MODEL` | − | Привязка к Django User (если есть) |
| `last_name` / `first_name` / `middle_name` | Char(128) | ✔/✔/− | ФИО (отчество опционально) |
| `email` | Email | − | Контактный e‑mail |
| `phone` | Char(32) | − | Телефон |
| `vk_user_id` | Char(64), `db_index` | − | VK/Max user id |

**Индексы:** по `vk_user_id`.  
**`__str__`**: `Фамилия Имя`.

---

### `Teacher`
**Назначение:** объект преподавателя, связан с университетом.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `person` | OneToOne → `Person` | ✔ |
| `academic_title` | Char(128) | − |
| `department` | Char(255) | − |
| `university` | FK → `University` | ✔ |

---

### `StudentGroup`
**Назначение:** студенческая группа (например, ПО‑51).  
> В dev допускается `null=True` у `university`; в продакшене лучше сделать обязательным.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `university` | FK → `University` | *в dev: −* |
| `program` | FK → `Program` | ✔ |
| `name` | Char(64) | ✔ |
| `admission_year` | PositiveSmallInteger | ✔ |
| `curator` | FK → `Teacher` (SET_NULL) | − |

**Ограничения:** `unique_together(program, name)` — имя группы уникально в рамках программы.  
**Индексы:** `admission_year`.

---

### `Student`
**Назначение:** студент (привязан к группе и вузу).

| Поле | Тип | Обяз. |
|---|---|:--:|
| `person` | OneToOne → `Person` | ✔ |
| `university` | FK → `University` | ✔ |
| `student_group` | FK → `StudentGroup` | ✔ |
| `student_id` | Char(32), `unique` | ✔ |
| `current_year` | PositiveSmallInteger (1..6) | ✔ |
| `admission_year` | PositiveSmallInteger | ✔ |

**Замечание:** `current_year` можно вычислять из даты зачисления/плана, но отдельное поле упрощает отчеты и фильтры.

---

### `University`
**Назначение:** университет.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `name` | Char(256), `unique` | ✔ |
| `short_name` | Char(64), `unique` | ✔ |
| `city` | Char(128) | − |
| `description` | Text | − |
| `contact_email` | Email | − |

---

### `Faculty`
**Назначение:** факультет/институт в рамках университета.  
> В продакшене рекомендуется сделать `university` обязательным.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `university` | FK → `University` | *в dev: −* |
| `name` | Char(256) | ✔ |

---

### `Program`
**Назначение:** образовательная программа.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `faculty` | FK → `Faculty` | ✔ |
| `name` | Char(255) | ✔ |
| `code` | Char(32) | − |
| `duration_years` | PositiveSmallInteger (default=4) | − |

**Ограничения:** `unique_together(faculty, name)`.

---

### `Discipline`
**Назначение:** дисциплина (ООП, Математика и т. п.).

| Поле | Тип | Обяз. |
|---|---|:--:|
| `code` | Char(32) | − |
| `title` | Char(256) | ✔ |
| `ects` | Decimal(4,1) | − |

**Ограничения:** `unique_together(code, title)`.

---

### `Curriculum`
**Назначение:** учебный план: в каком семестре и на какой программе читается дисциплина.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `program` | FK → `Program` | ✔ |
| `discipline` | FK → `Discipline` | ✔ |
| `semester` | PositiveSmallInteger (1..12) | ✔ |
| `hours` | PositiveSmallInteger | − |
| `control_form` | Char(32): exam/test/diff_test | − |

**Ограничения:** `unique_together(program, discipline, semester)`.

---

### `Teaching`
**Назначение:** конкретный курс в конкретный учебный год и семестр (кто ведёт и для какой группы).

| Поле | Тип | Обяз. |
|---|---|:--:|
| `teacher` | FK → `Teacher` | ✔ |
| `curriculum` | FK → `Curriculum` | ✔ |
| `group` | FK → `StudentGroup` (SET_NULL) | − |
| `academic_year` | Char(9) (`YYYY/YYYY`) | ✔ |
| `semester_in_year` | PositiveSmallInteger (1=осенний, 2=весенний) | ✔ |

**Ограничения:** `unique_together(teacher, curriculum, group, academic_year)`.  
**Индексы:** по `academic_year`.

---

### 'Role'

**Назначение:** временное решение для выдачи ролей Person

| Поле          | Тип | Обяз. |
|---------------|---|:--:|
| `permission ` | Char(32) | ✔ |
| `name`        | Char(32) | ✔ |

**permission:** - фактические права администрирования
**name:** - название прав

### `StudentRole`
**Назначение:** роли студента (староста, журналист, профорг) с периодом действия.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `student` | FK → `Student` | ✔ |
| `role` | Char(32): headman/journalist/TUO | ✔ |
| `start_date` | Date | ✔ |
| `end_date` | Date (nullable) | − |

**Индексы:** `(role, start_date)`.

---

### `Enrollment`
**Назначение:** факт зачисления студента на конкретное `Teaching`.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `student` | FK → `Student` | ✔ |
| `teaching` | FK → `Teaching` (PROTECT) | ✔ |
| `date_enrolled` | Date (auto_now_add) | ✔ |
| `is_active` | Boolean | ✔ |

**Ограничения:** `unique_together(student, teaching)`.  
**Индексы:** `is_active`.

---

### `Assessment`
**Назначение:** элемент оценивания в рамках `Teaching` (ДЗ/тест/лаб/экзамен/проект).

| Поле | Тип | Обяз. |
|---|---|:--:|
| `teaching` | FK → `Teaching` | ✔ |
| `title` | Char(255) | ✔ |
| `type` | Char(16): hw/quiz/lab/exam/project/other | ✔ |
| `max_points` | Decimal(6,2) (default=100) | − |
| `weight` | Decimal(5,2) (default=1.00) | − |
| `due_at` | DateTime | − |
| `is_final` | Boolean | − |

---

### `AssessmentResult`
**Назначение:** результат студента по элементу оценивания; поддерживаются попытки/пересдачи.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `assessment` | FK → `Assessment` | ✔ |
| `student` | FK → `Student` | ✔ |
| `attempt` | PositiveSmallInteger (нач. 1) | ✔ |
| `points` | Decimal(6,2) | ✔ |
| `graded_at` | DateTime (auto_now_add) | ✔ |
| `grade_5` | PositiveSmallInteger (2..5) | − |
| `grade_ects` | Char(2): A/B/C/D/E/FX/F | − |

**Ограничения:** `unique_together(assessment, student, attempt)`.  
**Индексы:** `(student, graded_at)`.

---

### `StudentRequest`
**Назначение:** заявления студента (включая справки), привязаны к университету.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `university` | FK → `University` | ✔ |
| `student` | FK → `Student` | ✔ |
| `type` | Char(64): certificate_enrollment/certificate_income/dormitory/practice/other | ✔ |
| `status` | Char(32): draft/submitted/in_progress/approved/rejected/issued | ✔ |
| `created_at` / `updated_at` | DateTime | ✔ |
| `payload_json` | JSON | − |

---

### `TeacherRequest`
**Назначение:** заявления преподавателя (включая отпуска/командировки), привязаны к университету.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `university` | FK → `University` | ✔ |
| `teacher` | FK → `Teacher` | ✔ |
| `type` | Char(64): annual/sick/academic/business/other | ✔ |
| `status` | Char(16): submitted/in_review/approved/rejected | ✔ |
| `created_at` / `updated_at` | DateTime | ✔ |
| `payload_json` | JSON | − |

---

### `Applicant`
**Назначение:** абитуриент; может быть связан со студентом после зачисления.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `person` | OneToOne → `Person` | ✔ |
| `birth_date` | Date | − |
| `passport_number` | Char(64) | − |
| `address` | Char(255) | − |
| `school_name` | Char(255) | − |
| `graduation_year` | PositiveSmallInteger | − |
| `linked_student` | OneToOne → `Student` (SET_NULL) | − |

---

### `ApplicantExam`
**Назначение:** результаты ЕГЭ/внутренних испытаний.

| Поле | Тип | Обяз. |
|---|---|:--:|
| `applicant` | FK → `Applicant` | ✔ |
| `subject` | Char(128) | ✔ |
| `exam_type` | Char(16): USE/internal/other | ✔ |
| `score` | Decimal(5,2) | ✔ |

**Ограничения:** `unique_together(applicant, subject, exam_type)`.

---

### `AdmissionRequest`
**Назначение:** заявка абитуриента на программу (приоритеты и статус).

| Поле | Тип | Обяз. |
|---|---|:--:|
| `applicant` | FK → `Applicant` | ✔ |
| `program` | FK → `Program` (PROTECT) | ✔ |
| `priority` | PositiveSmallInteger (default=1) | ✔ |
| `status` | Char(16): draft/submitted/under_review/accepted/rejected/enrolled | ✔ |
| `submitted_at` | DateTime (auto_now_add) | ✔ |
| `payload_json` | JSON | − |

**Ограничения:** `unique_together(applicant, program)`; индексы `(status, priority)`.

---

## Индексы и уникальные ограничения

- Уникальные: `Student.student_id`, наборы `unique_together` в `StudentGroup`, `Curriculum`, `Teaching`, `Enrollment`, `ApplicantExam`, `AdmissionRequest`.
- Индексы: по частым фильтрам — `vk_user_id`, `admission_year`, `academic_year`, `is_active`, `status`/`priority` и др.

---

## Типовые запросы (QuerySet)

```python
# Студенты вуза по группе:
Student.objects.filter(university=university, student_group=group)

# Дисциплины студента в учебном году:
Teaching.objects.filter(enrollments__student=student, academic_year="2025/2026").select_related("curriculum__discipline")

# Итог по курсу (нормированная сумма баллов):
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
total = (
    AssessmentResult.objects
    .filter(assessment__teaching=teaching, student=student)
    .annotate(part=ExpressionWrapper(
        F("points") / F("assessment__max_points") * F("assessment__weight"),
        output_field=DecimalField(max_digits=8, decimal_places=4)
    ))
    .aggregate(total=Sum("part"))["total"]
)

# Действующие роли сегодня:
from django.utils.timezone import now
today = now().date()
StudentRole.objects.filter(
    start_date__lte=today
).filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=today))

# Активные зачисления в семестре:
Enrollment.objects.filter(is_active=True, teaching__semester_in_year=1, teaching__academic_year="2025/2026")
```

---

## Валидация и бизнес-правила

- `AssessmentResult.points` ≤ `Assessment.max_points` — добавить кастомный `clean()` или `Constraint`.
- Сумма `weight` по `Assessment` в рамках одного `Teaching` может быть 1.0 **или** 100 — регламентируйте и валидируйте.
- `StudentRole`: (по желанию) запретить пересечение периодов одной роли у одного студента.
- `Teaching`: ограничение `unique_together` уже предотвращает дубли «проводки».

---

## Рекомендации по админке

- `search_fields`: ФИО (`person__last_name`, `person__first_name`), `student_id`, `program__name`, `discipline__title`.
- `list_filter`: `university`, `faculty`, `program`, `admission_year`, `academic_year`, `semester_in_year`, статусы заявлений.
- `autocomplete_fields`: все FK с большим кардиналитетом (`student`, `teacher`, `curriculum`, `program`).
- Для `payload_json` добавить простые формы/валидаторы или JSONSchema.

---

## Переносимость и миграции

- **SQLite** — подходит на старте/разработке.  
- **PostgreSQL** — предпочтительно в проде (JSONB, частичные индексы, CHECK).  
- Миграции: при правке `choices` (например, `ApplicantExam.EXAM_TYPE`) не забывайте **обновлять данные** и фикстуры.

---

## Дорожная карта расширений

- Расписание занятий: `ClassSession` (datetime, аудитория/ссылка), посещаемость `Attendance`.
- Материалы курса/прикрепления: `LearningMaterial`, файлы, дедлайны.
- Кэш итогов в `Enrollment` (`final_score_cached`) и периодический пересчёт.
- Процессы согласования заявлений (workflow с этапами/ролями).
- Интеграция с VK/Max: хранить IDs сообществ и чатов на уровне `University`; webhooks.

---