from settings import TOKEN
import telebot
from telebot import types
import datetime
import os
from my_functions import get_user_state, change_user_state, get_tasks, save_tasks, task_list_to_str
import pickle

bot = telebot.TeleBot(TOKEN)
emptyPhoto = 'https://image.prntscr.com/image/kC8tDU8nRkOnJNd5d-TRjw.png'


# ==== КОМАНДЫ START/HELP==== #

@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        l = os.listdir('users')
    except:
        os.mkdir('users')
        l = []
    if str(message.from_user.id)+'.pickle' not in l:
        save_tasks([], message.from_user.id)
        bot.send_message(message.chat.id, 'Привет! Если мне не изменяет память, мы не знакомы. Я -- бот для списков дел. Я уже создал отдельный список для твоих задач, так что давай начнём!')
    else:
        bot.send_message(message.chat.id, 'Хочешь начать всё сначала? (пока эта функция не работает, поэтому просто вызову /help)')
    help_handler(message)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot.send_message(message.chat.id, u'Команды (каждую команду можно вызвать без аргумента): \n\n/new\_item\n`/new_item {название_задачи}` -- добавить новую задачу\n\n/all\n`/all` -- посмотреть список задач в формате\n\n/show\_task\n`/show_task {номер задачи}` -- посмотреть задачу с её фото (или чем-то ещё)\n\n/delete\n`/delete {номер задачи}` -- удалить задачу с заданным номером (после этого все задачи с бОльшим номером опустятся)\n\n/done\n`/done {номер задачи}` -- сделать задачу выполненной\n\n/undone\n`/undone {номер задачи}` -- вернуть задачу (к невыполненным)\n\n/export\n`/export` -- получить .pickle файл с задачами (может быть полезным для следующей команды)\n\n/import\n`/import` -- ввести задачи из файла\n\n/state\n`/state` -- узнать, какая команда ожидает аргумент (idle значит нет ожидающей команды)\n\n/cancel\n`/cancel` -- убрать ожидание.', parse_mode='markdown')


# ==== ДОБАВЛЕНИЕ НОВОЙ ЗАДАЧИ ==== #

@bot.message_handler(commands=['new_item'], content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def new_item_handler(message):
    try:
        task_name = message.text.replace('/new_item ', '')
    except:
        task_name = None

    if task_name == '/new_item':
        bot.send_message(message.chat.id, 'Как называется новая задача?')
        change_user_state(message.from_user.id, 'new_item')
        return
        
    tasks = get_tasks(message.from_user.id)
    
    summary = task_name
    if summary == None:
        summary = message.caption.replace('/new_item ', '')

    media = None
    ct = message.content_type
    if ct != 'text':
            media = (ct, eval('message.'+ct)[0].file_id)
            
    # summary: str, isDone: bool, media: tuple, creation_date: str, completion_date: str, message_id: str
    tasks.append([summary, False, media, str(datetime.datetime.now())[:-7], None, message.message_id])
    
    n = len(tasks)

    save_tasks(tasks, message.from_user.id)

    bot.send_message(message.chat.id, 'Задача номер ' + str(n-1) + ' успешно добавлена!', parse_mode='html')


# ==== ОТОБРАЖЕНИЕ ОДНОЙ ЗАДАЧИ ==== #

@bot.message_handler(commands=['show_task'])
def show_task_handler(message, replace=False, task_number=None, user_id=None):
    '''Показывает сообщение с картинкой (даже если картинка не была прикреплена);
    эта функция вызывается также с помощью кнопки, поэтому ей нужно знать task_number и user_id'''

    if type(task_number) != int:
        task_number = message.text.replace('/show_task ', '')
    
    if task_number == '/show_task':
        bot.send_message(message.chat.id, 'Какой номер у задачи, которую мне нужно показать?')
        change_user_state(message.from_user.id, 'show_task')
        return
    
    task_number = int(task_number)

    if user_id == None:
        user_id = message.from_user.id
    tasks = get_tasks(user_id)
    task = tasks[task_number]
    task_text = str(task_number) + ') ' + task[0] + '\n\n🕰 Добавлена: ' + task[3]
    if task[1]:
        task_text += '\n✅ Выполнена: ' + task[4]
    
    if task[2]:
        content_type, file_id = task[2]

        if replace:
            showed_task = eval(f'bot.edit_message_media(types.InputMedia{content_type.capitalize()}(file_id, caption=task_text), message.chat.id, message.message_id)')
        else:
            showed_task = eval(f'bot.send_{content_type}(message.chat.id, {content_type}={repr(file_id)}, caption={repr(task_text)})')
        
    else:
        if replace:
            try:
                showed_task = bot.edit_message_media(types.InputMediaPhoto(emptyPhoto, caption=task_text), message.chat.id, message.message_id)
            except:                
                showed_task = bot.edit_message_caption(task_text+'`!`', message.chat.id, message.message_id, parse_mode='markdown')
        else:
            showed_task = bot.send_photo(message.chat.id, emptyPhoto, task_text)
    

    message_id = ':'+str(showed_task.message_id)
    chat_id = ':'+str(showed_task.chat.id)
    user_id = ':'+str(user_id)

    next_number = (task_number+1)%len(tasks)
    prev_number = (task_number-1)%len(tasks)
    
    keyboard = types.InlineKeyboardMarkup()
    callback_button_next = types.InlineKeyboardButton(text='>>', callback_data='show:'+str(next_number)+message_id+chat_id+user_id)
    callback_button_previous = types.InlineKeyboardButton(text='<<', callback_data='show:'+str(prev_number)+message_id+chat_id+user_id)
    callback_button_done = types.InlineKeyboardButton(text='✅', callback_data='done:' + str(task_number)+message_id+chat_id+user_id)
    callback_button_link = types.InlineKeyboardButton(text='Показать сообщение', callback_data='reply:'+str(task[5])+chat_id+':.')
    
    keyboard.row(callback_button_previous, callback_button_done, callback_button_next)
    keyboard.add(callback_button_link)

    bot.edit_message_reply_markup(showed_task.chat.id, showed_task.message_id, reply_markup=keyboard)


# ==== ОБРАБОТКА НАЖАТИЙ НА КНОПКИ ==== #

@bot.callback_query_handler(func=lambda call: call.data.startswith('show'))
def show_callback_query_handler(call):
    task_number, message_id, chat_id, user_id = [int(x) for x in call.data.split(':')[1:]]
    message = bot.edit_message_reply_markup(chat_id, message_id)
    show_task_handler(message, True, task_number, user_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('done'))
def done_callback_query_handler(call):
    task_number, message_id, chat_id, user_id = [int(x) for x in call.data.split(':')[1:]]

    message = bot.edit_message_reply_markup(chat_id, message_id)
    tasks = get_tasks(user_id)

    tasks[task_number][1] = True
    tasks[task_number][4] = str(datetime.datetime.now())[:-7]
    save_tasks(tasks, user_id)

    show_task_handler(message, True, task_number, user_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reply'))
def reply_callback_query_handler(call):
    message_id, chat_id, text = call.data.split(':')[1:]
    message_id, chat_id = int(message_id), int(chat_id)
    bot.send_message(chat_id, text, reply_to_message_id=message_id)


# ==== КОМАНДА ALL ==== #

@bot.message_handler(commands=['all'])
def show_all_handler(message):
    '''Показать все задачи'''
    tasks = get_tasks(message.from_user.id)

    bot.send_message(message.chat.id, task_list_to_str(tasks), parse_mode='html')


# ==== КОМАНДЫ ИЗМЕНЕНИЯ/УДАЛЕНИЯ ==== #

@bot.message_handler(commands=['delete'])
def delete_handler(message):
    '''Удалить задачу по номеру'''
    task_number = message.text.replace('/delete ', '')

    if task_number == '/delete':
        bot.send_message(message.chat.id, 'Какой номер у задачи, которую нужно удалить?')
        change_user_state(message.from_user.id, 'delete')
        return
    
    task_number = int(task_number)
    
    tasks = get_tasks(message.from_user.id)
    try:
        deleted = tasks.pop(task_number)
    except:
        bot.send_message(message.chat.id, 'Задачи с таким номером нет! /all для просмотра всех задач.')
        return

    save_tasks(tasks, message.from_user.id)

    bot.send_message(message.chat.id, 'Задача ``` '+ deleted[0] + '``` успешно удалена!', parse_mode='markdown')


@bot.message_handler(commands=['done'])
def done_handler(message):
    '''Зачеркнуть задачу по номеру'''
    task_number = message.text.replace('/done ', '')

    if task_number == '/done':
        bot.send_message(message.chat.id, 'Какой номер у задачи, которую нужно зачеркнуть?')
        change_user_state(message.from_user.id, 'done')
        return
        
    task_number = int(task_number)
    tasks = get_tasks(message.from_user.id)
    tasks[task_number][1] = True
    tasks[task_number][4] = str(datetime.datetime.now())[:-7]
    
    save_tasks(tasks, message.from_user.id)
    
    bot.send_message(message.chat.id, 'Задача ``` '+ tasks[task_number][0] + '``` успешно зачёркнута!', parse_mode='markdown')


@bot.message_handler(commands=['undone'])
def undone_handler(message):
    '''Вернуть (к несделанным) задачу по номеру'''
    task_number = message.text.replace('/undone ', '')

    if task_number == '/undone':
        bot.send_message(message.chat.id, 'Какой номер у задачи, которую нужно вернуть?')
        change_user_state(message.from_user.id, 'undone')
        return

    task_number = int(task_number)
    tasks = get_tasks(message.from_user.id)
    tasks[task_number][1] = False
    tasks[task_number][4] = None
    save_tasks(tasks, message.from_user.id)

    
    bot.send_message(message.chat.id, 'Задача ``` '+ tasks[task_number][0] + '``` успешно возвращена!', parse_mode='markdown')


# ==== ЭКСПОРТ/ИМПОРТ ==== #

@bot.message_handler(commands=['export'])
def export_handler(message):
    '''Получение pickle файла с задачами, чтобы их можно было сохранить'''
    if message.text == '/export':
        task_file = 'users/' + str(message.from_user.id) + '.pickle'
        with open(task_file, 'rb') as f:
            bot.send_document(message.chat.id, f)
        return

@bot.message_handler(commands=['import'])
def import_handler(message):
    '''Ввод задач из файла'''
    if message.text == '/import':
        bot.send_message(message.chat.id, 'Отправьте файл с задачами (если файл сохранён с помощью pickle, то у файла должно быть .pickle)')
        change_user_state(message.from_user.id, 'import')
        return

    task_file = bot.get_file(message.document.file_id)
        
    f = bot.download_file(task_file.file_path)

    import_file_name = 'users/[import_file] '+ message.document.file_name
    
    with open(import_file_name, 'wb') as w:
        w.write(f)

    if import_file_name.endswith('.pickle'):
        with open(import_file_name, 'rb') as imf:
            new_tasks = pickle.load(imf)

        keyboard = types.InlineKeyboardMarkup()
        callback_button_yes = types.InlineKeyboardButton(text='Да', callback_data='import_yes:' + import_file_name)
        callback_button_no = types.InlineKeyboardButton(text='Нет', callback_data='import_no')
        callback_button_replace = types.InlineKeyboardButton(text='Заменить', callback_data='import_replace:' + import_file_name)

        keyboard.row(callback_button_yes, callback_button_no)
        keyboard.add(callback_button_replace)

        bot.send_message(message.chat.id, task_list_to_str(new_tasks), parse_mode='html')
        bot.send_message(message.chat.id, 'Добавить эти задачи к текущим?', reply_markup=keyboard)

# ==== ОБРАБОТКА КНОПОК ИМПОРТА ==== #

@bot.callback_query_handler(func=lambda call: (type(call.data) == str and ('import_yes' in call.data or 'import_replace' in call.data)))
def import_yes_replace_callback_query_handler(call):
    tasks = get_tasks(call.from_user.id)
    import_file_name = call.data.split(':')[1]

    with open(import_file_name, 'rb') as f:
        imported_tasks = pickle.load(f)

    if call.data.startswith('import_yes'):
        tasks += imported_tasks
        status_message = bot.send_message(call.from_user.id, 'Добавение...')
        response = 'да'
    else:
        tasks = imported_tasks
        status_message = bot.send_message(call.from_user.id, 'Замена...')
        response = 'заменить'
    
    save_tasks(tasks, call.from_user.id)
    os.remove(import_file_name)
    chat_id, message_id = status_message.chat.id, status_message.message_id

    bot.edit_message_text(status_message.text + ' Готово!', chat_id, message_id)

    bot.edit_message_text(call.message.text + ' (ваш ответ: '+response+')', call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())


@bot.callback_query_handler(func=lambda call: (call.data == 'import_no'))
def import_no_callback_query_handler(call):
    bot.edit_message_text(call.message.text + ' (ваш ответ: нет)', call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=types.InlineKeyboardMarkup())
    

# ==== КОМАНДЫ СОСТОЯНИЯ ==== #

@bot.message_handler(commands=['state'])
def check_my_state_handler(message):
    bot.send_message(message.chat.id, get_user_state(message.from_user.id))

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    bot.send_message(message.from_user.id, 'Отменена команда ' + get_user_state(message.from_user.id, True))    


# ==== ФУНКЦИЯ ДЛЯ ОБРАБОТКИ "РВАННОГО" ВЫЗОВА КОМАНДЫ ==== #

@bot.message_handler(func=lambda message: (get_user_state(message.from_user.id) != 'idle' and (message.text == None or '/' != message.text[0])), content_types=['audio', 'photo', 'voice', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def command_part_handler(message):
    '''Выполняет ожидающую аргумент команду после его получения (если он был отправлен отдельным сообщением)'''
    state = get_user_state(message.from_user.id, refresh=True)
    
    # какой-то обработчик вставится на место eval, затем сообщение обработается нужной функцией
    eval(state + '_handler')(message)
   


bot.polling(none_stop=True, interval=0, timeout=20)
