# Цифровой вуз — документация к `models.py` (подробно)

> База: **Django ORM**, СУБД: **SQLite** (совместимо с Postgres/MySQL)  
> Назначение: мультивузовый сервис (одна инсталляция — несколько университетов).  
> Версия файла: **1.1**

---

## Общая картина

Схема определяет **базовый класс** (`Person`) и **его наследников (роли)** (`Student`, `Teacher`, `Applicant`).  
Иерархия структур внутри университета: `University → Faculty → Program → StudentGroup`.  
Учебный план (`Curriculum`) и класс текущей учебной дисциплины (`Teaching`) описывают,
кто и в какой год/семестр ведёт дисциплину в конкретной группе.  
Система оценивания состоит из **элементов контроля** (`Assessment`) и **результатов** (`AssessmentResult`) в разрезе **зачислений** (`Enrollment`).  
Заявления унифицированы: `StudentRequest`, `TeacherRequest`. 
Абитуриенты: `Applicant`, результаты экзаменов `ApplicantExam` и заявки `AdmissionRequest`.

`University` — большинство сущностей прямо или косвенно связаны с конкретным вузом.

* Один `University` содержит много `Faculty`
* Один `Faculty` содержит много `Program`
* В `Program` есть учебный план `Curriculum` - какие `Discipline` читаются в каких семестрах
* `Teacher` читает `Teaching` по конкретному `Curriculum` для группы `StudentGroup` в учебный год
* Студенты (`Student`) принадлежат группе, и на курс их подключает `Enrollment`
* Оценивание - это `Assessment` и попытки `AssessmentResult`
* Расписание - повторяемые ячейки `ScheduleSlot` + разовые исключения `ScheduleException`
* Новости `NewsPost` и групповые уведомления `GroupNotification`
* Права доступа завязаны на `Role` и поле `role` в `Person`

### Упрощенная схема зависимостей

```
University
 ├─ Faculty (M:1 University)
 │   └─ Program (M:1 Faculty)
 │       └─ Curriculum (M:1 Program, M:1 Discipline)
 ├─ StudentGroup (M:1 University, M:1 Program, curator=Teacher?)
 │   └─ Student (M:1 University, M:1 StudentGroup, 1:1 Person)
 ├─ Teacher (1:1 Person, M:1 University)
 │   └─ Teaching (M:1 Teacher, M:1 Curriculum, M:1 StudentGroup?)
 │       ├─ Enrollment (M:1 Student, M:1 Teaching)
 │       └─ Assessment (M:1 Teaching)
 │           └─ AssessmentResult (M:1 Assessment, M:1 Student)
 ├─ ScheduleSlot (M:1 University, M:1 Teaching, M2M StudentGroup)
 │   └─ ScheduleException (M:1 ScheduleSlot)
 ├─ NewsPost (M:1 University)
 └─ GroupNotification (M:1 University, M:1 StudentGroup, M:1 Person)
```

---

## Все что связано с аккаунтом

### Person

* 1:1 к Django User - можно не связывать сразу
* `role` - ссылка на `Role`, упрощённая модель прав
* индекс по `vk_user_id` - быстрый поиск интеграции
* удаление `User` не удаляет `Person` - `SET_NULL`

**Типичные запросы**

```python
# Получить роль пользователя
role_code = person.role.permission if person.role else "Guest"

# Найти по внешнему VK/Max id
person = Person.objects.filter(vk_user_id=vk_id).first()
```

### Role

* `permission` - код уровня доступа
* возможные значения: Moderator_1lvl/2lvl/3lvl, Teacher, Student, Guest и т.д.

**Заметка**

* Это мост к авторизации на уровне views - удобно, пока не введена таблицу прав

### Teacher

* 1:1 с `Person`
* принадлежит конкретному `University`
* `department` - строкой, но при желании можно вынести в отдельную сущность

### StudentGroup

* у группы есть `program`, год набора и необязательный `curator` (Teacher)
* `unique_together (program, name)` - один и тот же код группы не повторяется в рамках программы
* индекс по `admission_year` - быстрые выборки потоков
* принадлежит `University` - это наш контур изоляции данных

### Student

* 1:1 с `Person`
* принадлежит `University` и `StudentGroup`
* есть `student_id` - уникальный номер билета
* `current_year` валидируется 1..6

---

## Университет и его составляющие

### University

* `name` и `short_name` - оба уникальны
* для красивых заголовков используем `short_name` если есть

### Faculty

* много факультетов в университете
* здесь `null=True` у `university` оставлен для разработки

### Program

* принадлежит `Faculty`
* `unique_together (faculty, name)` - одно название на факультет
* `code` - например 09.03.04

---

## Учебный контент

### Discipline

* код, название, ECTS
* `unique_together (code, title)`

### Curriculum

* какой `Discipline` читается в рамках `Program`, в каком семестре и как контролируется
* `unique_together (program, discipline, semester)` - дисциплина не дублируется в одном семестре
* `control_form` - exam/test/diff_test

### Teaching

* связывает `Teacher` + `Curriculum` + `StudentGroup?` + учебный год и семестр
* `group` может быть пустой - тогда это поток, и расписание можно привязать через M2M в `ScheduleSlot`
* `unique_together (teacher, curriculum, group, academic_year)` - исключаем дубль одного и того же курса
* индекс по `academic_year` - частый фильтр

**Типичные сценарии**

```python
# Все курсы преподавателя в этом году
Teaching.objects.filter(teacher=teacher, academic_year="2025/2026")

# Все курсы группы
Teaching.objects.filter(group=group)
```

---

## Роли (На модели из этого блока будет заменена модель Role)

### StudentRole

* роль типа headman/journalist/TUO
* хранит историю периодов (start_date - end_date)
* индекс по `(role, start_date)` - быстрые «активные на дату» выборки

---

## Система оценивания

### Enrollment

* факт, что студент записан на `Teaching`
* `unique_together (student, teaching)` - без дублирования
* удобно массово создавать после создания `Teaching` для группы

### Assessment

* элемент оценивания в курсе: тип, вес, дедлайн
* `weight` - для итоговой агрегации

### AssessmentResult

* попытки у студента по каждому `Assessment`
* `unique_together (assessment, student, attempt)`

**Пример агрегации**

```python
# Сумма набранных баллов по курсу
from django.db.models import Sum
total = (AssessmentResult.objects
         .filter(student=student, assessment__teaching=teaching)
         .aggregate(total=Sum("points"))["total"] or 0)
```

---

## Новости и уведомления

### NewsPost

* новость по университету
* хранит эмодзи, заголовок, текст, автора, обложку
* `ordering = -published_at`
* `get_absolute_url` - для роутинга

### GroupNotification

* сообщение только для одной группы
* отправитель - любой `Person` (обычно Teacher или headman)
* в `clean()` проверяется согласованность университета у группы и у записи
* индексы по `(group, created_at)` - свежие уведомления для группы достаются быстро

---

## Расписание

Нормализовано на два уровня:

* `ScheduleSlot` - повторяющаяся пара (по дню недели, времени, чётности и диапазону дат)
* `ScheduleException` - разовое событие: отмена - перенос - смена аудитории/примечания

### ScheduleSlot

* принадлежит `University` и `Teaching`
* M2M `groups` - можно повесить слот сразу на несколько групп (поток)
* `weekday` 1..7 - понедельник..воскресенье
* `week_parity` all/odd/even - поддержка верхней/нижней недели
* `start_date` - `end_date` - временной коридор валидируется
* индексы по `(university, weekday, start_time)` и `(start_date, end_date)`

**Ключевая логика**

* `clean()` - проверяет валидность времени/дат и что `Teaching.teacher.university == university`
* `applies_on_date(date, term_start=None)` - проверяет, попадает ли дата по дню и чётности
* `effective_for_date(date)` - возвращает итоговые параметры пары с учётом исключения на эту дату

```python
is_cancelled, start, end, bld, room, note, eff_date = slot.effective_for_date(today)
```

### ScheduleException

* `cancel` - отмена пары
* `move` - перенос на новую дату/время/аудиторию
* `change_room` - только смена аудитории/примечания
* `clean()` заставляет заполнить нужные поля для каждого action
* индекс по `(date, action)` - выборки на день

**Подбор слотов для группы на неделю**

```python
from django.db.models import Q
week_slots = (ScheduleSlot.objects
  .filter(university=group.university)
  .filter(Q(groups__id=group.id) | Q(teaching__group_id=group.id))
  .select_related("teaching", "teaching__curriculum", "teaching__curriculum__discipline",
                  "teaching__teacher", "teaching__teacher__person")
  .prefetch_related("groups", "exceptions")
  .distinct()
  .order_by("weekday", "start_time"))
```

---

## Абитуриенты и приём

### Applicant / ApplicantExam

* анкета абитуриента и результаты экзаменов
* `unique_together (applicant, subject, exam_type)` - один предмет - один тип оценки

### AdmissionRequest / ApplicationRequest

* у нас есть две формы подачи - исторически сложилось
* обе содержат контакты, желаемую программу и статус обработки
* эти модели используются для входящих заявок на зачисление

---

## Инварианты и валидации

* Во многих местах заданы `unique_together` - не игнорируем сообщения БД при миграциях
* `ScheduleSlot.clean()` - гарантирует непротиворечивость времени - дат - университетов
* `GroupNotification.clean()` - группа и университет должны совпадать
* Поля со связями на `University` - наши границы мульти-тенантности

---

## Производительность и индексы

* Индексы поставлены там, где у нас регулярные фильтры:

  * `vk_user_id` для интеграции
  * `StudentGroup.admission_year` - разрезы по наборам
  * `Teaching.academic_year`
  * `ScheduleSlot (university, weekday, start_time)` - быстрые выборки по сетке
  * `ScheduleSlot (start_date, end_date)` - попадание в интервал
  * `GroupNotification (group, created_at)` - лента уведомлений группы
  * `AssessmentResult (student, graded_at)` - история оценок

---

## Жизненный цикл сущностей

* Создаём `Teaching` для группы - после сохранения обычно делаем массовый `Enrollment`
* Меняем `Teacher` у `Teaching` - слоты расписания остаются валидными, если университет тот же
* Удаляем `Teacher` - каскадно удалятся его `Teaching`, а дальше по цепочке - аккуратно с продом
* Удаляем `StudentGroup` - каскадами уйдут `Student`, `Teaching.group`, M2M в слотах тоже очистится
* Практика - крупные удаления закрываем предварительной проверкой ссылок и soft-delete, если потребуется

---

## Примеры частых операций

### Массовая запись студентов группы на курс

```python
from django.db import transaction
students = Student.objects.filter(student_group=group)

with transaction.atomic():
    created = 0
    for s in students:
        _, was_created = Enrollment.objects.get_or_create(student=s, teaching=teaching)
        created += int(was_created)
print(f"Подключили {created} студентов")
```

### Вытянуть расписание студента на сегодня

```python
today = timezone.localdate()
slots = (ScheduleSlot.objects
         .filter(university=student.university)
         .filter(Q(groups__id=student.student_group_id) | Q(teaching__group_id=student.student_group_id))
         .select_related("teaching__curriculum__discipline")
         .prefetch_related("exceptions")
         .distinct())

today_pairs = []
for slot in slots:
    eff = slot.effective_for_date(today)
    if eff:
        is_cancelled, start, end, bld, room, note, _ = eff
        if not is_cancelled:
            today_pairs.append((slot, start, end, bld, room, note))
```

### Поиск дисциплин

```python
q = "ООП"
disciplines = Discipline.objects.filter(Q(title__icontains=q) | Q(code__icontains=q))
```