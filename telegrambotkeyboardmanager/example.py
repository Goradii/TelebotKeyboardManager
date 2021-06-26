from telegrambotkeyboardmanager.TeleBotKM import *
import telebot


# и так, создадим нашего бота
bot = telebot.TeleBot('TOKEN')

# теперь назначим ему админа
admin = KeyboardAdministrator(bot)

# менеджеры не зависят от админа, но прикреплены к боту, создадаим двоих
admin_chat = KeyboardManager(bot, parse_mode='HTML')
main_chat = KeyboardManager(bot, parse_mode='HTML')

# пришло время определить наши клавиатуры, однако клавиатуру невозможно определить без кнопок, так что самое время создать несколько

# !! обратите внимание, у всех кнопок на одной клавиатуре должен быть разный текст
# наша первая кнопка, будет иметь текст "Hi", и вызывать событие "hi"
hi_btn = Button('Hi', ':call>>hi')

# и первая клавиатура, при активации отправит сообщение с текстом 'Hello', и покажет нашу кнопку
hi_kb = Keyboard('Hello', [[hi_btn]])

# клавиатуру можно использовать самостоятельно вызывая приватный метод _show можно но лучше передать ее менеджеру, 'hi' ключ клавиатуры, по нему менеджер отобразит ее при запросе
# entry это параметр указывающий на то, что менеджер начнет свою работу с этой клавиатуры
main_chat.add_keyboard('hi', hi_kb, entry=True)

# так же, можно не создавать клавиатуру заранее, и использовать одну из стандартных кнопок start_btn, она выведет пользователю команду для перезапуска бота
main_chat.new_keyboard('bye', 'It was nice to talk to you', [[start_btn]])

# теперь менеджер управляет двумя клавиатурами, но пока он не может между ними переключаться, исправим это упущение


@admin.handler.event('hi')  # создадим событие 'hi' которое вызывает наша кнопка
def hi_btn_processor(message):  # все события и функции передающиеся кнопкам должны получать один параметр (telebot.types.Message)
    return ':goto>>bye'  # к сожалению за отсутствием функционала просто вызовем клвиатуру с ключем 'bye'


@bot.message_handler(commands=['start'])
def start_bot(message):
    admin.start(message, main_chat)  # запускаем админа и передаем ему message и менеджера который должен начать работу


@bot.message_handler(content_types=['text'])
def send_text(message):
    admin.reply(message)  # админ должен ответить на сообщение пользователя


bot.polling(none_stop=True, interval=0)
