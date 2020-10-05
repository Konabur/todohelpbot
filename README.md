# todohelpbot
Бот для создания и выполнения задач to-do

## Запуск
Для запуска нужно:
1) Клонировать репозиторий в папку\
 *необязательно* Создать в папке виртуальную оболочку "python -m venv venv"
2) Запустить в консоли "pip install -r requirements.txt"
3) Запустить файл main.py "python main.py"
4) Готово! Теперь можно написать боту по ссылке https://t.me/todohelpbot

## Фишки
- Каждую команду можно вызвать как сразу с аргументами (сделано с помощью состояний, о них позже), так и без, что удобно, если команда вызывается по ссылке
- Можно сохранить текущую версию задач, чтобы сделать резервную копию, которую легко импортировать обратно
- Просмотр задач по одной в одном сообщении с помощью кнопок
- Каждая задача имеет ровно одно фото (вместо фото может быть видео, документ и т. п.), дату создания и дату выполнения (последнюю можно менять)
- Каждая задача хранит в себе ссылку на сообщение, по которому она была создана, может быть полезно, если было несколько фото или видео

## Команды
### start - Инициализация нового пользователя
*Пока что работает только для нового пользователя*
Создаёт пустой файл, в котором будут храниться задачи
### help - Примеры использования команд
Примеры вызовов команд с аргументом
### new_item - Добавить новую задачу
Добавляет новую задачу в список, каждая задача является списком, имеющим вид 
task = [summary, is_done. media, creation_date, completion_date, message_id]
- summary - str - Описание задачи
- is_done - bool - Статус задачи
- media - tuple(content_type: str, file_id: str) - Прикреплённый к задаче файл, описанный типом и идентификатором, по которому его можно получить
- creation_date - str - Дата создания, создаётся с помощью datetime.datetime.now()
- completion_date - str (по умол. None) - Дата выполнения, создаётся с помощью datetime.datetime.now()
- message_id - int - Номер сообщения, по которому была создана задача
### show_task - Показать задачу, зная её номер
Отображает полную информацию о задаче (описание, медиа, дата создания и (если есть) дата выполнения)). Отображение следующей/предыдущей задачи происходит через редактирование заголовка (caption) и медиа, а также кнопок. Кнопки загружаются в самом конце, поэтому немного тормозят. У сообщения с отображённой задачей есть 4 кнопки:
- '<<' - Показать предыдующую задачу (номер текущей-1)
- '✅' - Отметить как выполненную
- '>>' - Показать следующую задачу (номер текущей+1)
- 'Показать сообщение' - Бот отправляет ответ на сообщение, по которому была создана эта задача.
### all - Показать все задачи 
Выводит список задач, сделанные отделены от остальных
### delete - Удалить задачу, зная номер
Удаляет сообщение по номеру, если такая задача есть, показывает её описание
### done - Зачеркнуть задачу
Отмечает задачу как выполненную, т.е. is_done стаовится равным True, дата выполнения меняется на текущие дату и время
### undone - Вернуть
Отмечает задачу, как невыполненную, is_done становится равным False
### export - Скачать файл с задачами
Отправляет файл {user_id}.pickle, который можно будет импортировать позже
### import - Загрузить файл с задачами
Получает файл .pickle (имя не имеет значения), отображает задачи из файла, которые можно добавить, на них можно заменить текущие или ничего не делать, если что-то пошло не так.
### state - Узнать состояние
Возвращает состояние (т. е. последнюю команду, которая ещё не до конца обработана).
Состояние равно 'idle', если ни какой команды бот не ждёт
Если была вызвана какая-то команда без аргумента, состоние меняется на эту команду, чтобы напомнить боту, что нужно ещё получить аргумент
### cancel - Очистить состояние
Сделать состояние равным 'idle'
