# МОДУЛЬ ФУНКЦИЙ ДЛЯ РАБОТЫ С ФАЙЛАМИ + ОТОБРАЖЕНИЯ СПИСКА ЗАДАЧ
import pickle

# ==== РАБОТА С ОЖИДАНИЯМИ (СОСТОЯНИЯМИ) ==== #

def get_user_state(user_id: int, refresh=False, states_path='states.pickle') -> str:
    '''Возвращает состояние (тип ожидаемого сообщения от) пользователя, если ничего не ожидается, то состояние idle;
    refresh нужен для сброса состояния, когда нужное сообщение принято'''
    try:
        with open(states_path, 'rb') as f:
            states: dict = pickle.load(f)
    except:
        states = {}

    if user_id in states:
        state = states[user_id]
    else:
        state = 'idle'
    
    if refresh:
        states[user_id] = 'idle'
        with open(states_path, 'wb') as f:
            pickle.dump(states, f)

    return state

def change_user_state(user_id: int, new_state: str, states_path='states.pickle'):
    '''Меняет состояние пользователя (то, что он должен отправить), чтобы правильно определить тип следующего сообщения'''
    try:
        with open(states_path, 'rb') as f:
            states: dict = pickle.load(f)
    except:
        states = {}
    
    states[user_id] = new_state

    with open(states_path, 'wb') as f:
        pickle.dump(states, f)


# ==== РАБОТА С ФАЙЛОМ СПИСКА ЗАДАЧ ==== #

def get_tasks(user_id: int) -> list:
    '''Возвращает список задач пользователя user_id'''
    file_path = 'users/' + str(user_id) + '.pickle'
    with open(file_path, 'rb') as f:
        try:
            return pickle.load(f)
        except:
            return []
    
def save_tasks(tasks: list, user_id: int):
    '''Сохраняет список задач tasks пользователя user_id'''
    file_path = 'users/' + str(user_id) + '.pickle'
    with open(file_path, 'wb') as f:
        pickle.dump(tasks, f)

def task_list_to_str(tasks: list) -> str:
    '''Возвращает строку, в которой каждая задача пронумерована и выполненные задачи вынесены отдельно'''
    task_list = done_list = '\n'
    i = 0
    for task in tasks:
        if task[1]:
            # зачёркиваем каждую выполненную задачу с п-ю <s>...</s>
            done_list += str(i) + ')✅ <s>' + task[0] + '</s>' + '\n'
        else:
            task_list += str(i) + ') ' + task[0] + '\n'
        i += 1
    
    result = 'Сделанные:' + done_list + '\nОставшиеся:' + task_list

    return result
