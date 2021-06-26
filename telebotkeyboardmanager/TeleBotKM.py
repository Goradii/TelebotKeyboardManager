from telebot import types, TeleBot
from typing import Union


class _EventHandler:

    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_EventHandler, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not _EventHandler._inited:
            self.handlers = {}
            _EventHandler._inited = True

    def event(self, event: str):
        """ @Decorator \n
        Handle the event \n
        handled func must receive at least one parameter: types.Message \n
        --\n
        func can return commands: \n
        -   ':goto>>%keyboard_name%' to activate Keyboard in manager \n
        -   ':back:' to return to previous Keyboard \n
        -   ':home:' to return to entry Keyboard \n
        -   ':msg>>%message_text%' to send a message \n

        :param event:
        :return: command str
        """
        def register_handler(handler):
            self.handlers[event] = handler
            return handler
        return register_handler

    def call(self, message: types.Message, event, *args, **kwargs):
        """
        Call event

        :param message:
        :param event:
        """
        if event in self.handlers:
            r = self.handlers[event](message, *args, **kwargs)
            if r:
                return r
        else:
            print(f'Unhandled call: {event}')


class Button:

    def __init__(self, text: str, data: Union[str, types.InlineKeyboardButton, types.KeyboardButton], *args, **kwargs):
        """
        Button for Keyboard \n
        --\n
        Use data param to setup command \n
        -   ':call>>%event_name%' to trigger the event \n
        -   ':err>>%error_message%' to print in terminal \n
        -   ':goto>>%keyboard_name%' to activate Keyboard in manager \n
        -   ':back:' to return to previous Keyboard \n
        -   ':home:' to return to entry Keyboard \n
        -   ':msg>>%message_text%' to send a message \n


        You can combine commands with ':>>' transition (':call>>' and '"err>>' can not be combined) \n
        -   Example: ':msg>>Hello:>>:goto>>keyboard' \n

        Or use data param to setup KeyboardButton and setup Keyboard.user_input_handler() with Button, to handle specific reply \n
        Or to setup InLineKeyboardButton use .call_back_data to setup command \n


        :param text: Button text & uniq name in Keyboard
        :param data: command string
        :param *args: to ':call>>%event_name%'
        """
        self.text = text
        self.data = data
        self.args = args
        self.kwargs = kwargs
        if type(self.data) is types.KeyboardButton or type(self.data) is types.InlineKeyboardButton:
            self.text = self.data.text

    def _get_reply(self):
        if type(self.data) is types.KeyboardButton:
            return self.data
        elif type(self.data) is types.InlineKeyboardButton:
            raise ValueError('This Button specified as InlineKeyboardButton (for InLineKeyboardMarkup only), can\'t use in ReplyKeyboardMarkup')
        else:
            return types.KeyboardButton(self.text)

    def _get_inline(self):
        if type(self.data) is types.InlineKeyboardButton:
            return self.data
        elif type(self.data) is types.KeyboardButton:
            raise ValueError('This Button specified as KeyboardButton (for ReplyKeyboardMarkup only), can\'t use in InLineKeyboardMarkup')
        else:
            return types.InlineKeyboardButton(text=self.text, callback_data=self.text)

    def _press(self, message):
        if type(self.data) is str:
            for caommand in self.data.split(':>>'):
                if ':call>>' in caommand:
                    return _EventHandler().call(message, caommand.split('>>')[1], *self.args, **self.kwargs)
                elif ':err>>' in caommand:
                    print(self.data)
                    return ''
            return self.data
        elif type(self.data) is types.InlineKeyboardButton:
            return self.data.callback_data
        elif type(self.data) is types.KeyboardButton:
            return self.data.text
        else:
            print(f'Unknown object {self.data}')


_error_message = 'Button is undefined or deprecated. Use /start to restart the bot'
back_btn = Button('Back', ':back:')
home_btn = Button('Home', ':home:')
start_btn = Button('Start', ':msg>>/start')


def set_err_msg(msg):
    global _error_message
    _error_message = str(msg)


class Keyboard:

    def __init__(self, msg: str, rows: list, row_width: int = 3, user_input_handler=None):
        """
        Keyboard for KeyboardsManager \n

        :param msg: Text of message, show when keyboard appears
        :param rows: list of rows: list, one row contains a Buttons
        :param row_width: default row width
        :param user_input_handler: Button or Button command
        """
        self.keyboard = None
        self.row_width = row_width
        self.message_text = msg
        if user_input_handler:
            self.user_input_handler(user_input_handler)
        else:
            self._cmd_btn = Button('__', 'Default user input handler')
        self._buttons = {}
        self._markup = []
        for row in rows:
            self._markup.append(len(row))
            for btn in row:
                self._new_button(btn)

    def user_input_handler(self, btn: Button):
        """
        Handle user input with Button or Button command.
        This button will not be shown to the user.

        :param btn: Button or Button command
        :return: Keyboard obj
        """
        if type(btn) is Button:
            self._cmd_btn = btn
        elif type(btn) is str:
            self._cmd_btn = Button('__', btn)
        else:
            raise ValueError('User input handler must be Button or str')
        return self

    def _new_button(self, btn):
        if type(btn) is Button:
            self._buttons[btn.text] = btn
        elif type(btn) is types.InlineKeyboardButton:
            self._buttons[btn.text] = Button(btn.text, btn)
        elif type(btn) is types.KeyboardButton:
            self._buttons[btn.text] = Button(btn.text, btn)
        else:
            raise ValueError("'button' must be Button, InlineKeyboardButton, KeyboardButton")

    def _rows_compose(self, keyboard_markup_obj, kb_type):
        self.keyboard = keyboard_markup_obj
        row_number = 0
        row_fill = self._markup[row_number]
        row = []
        for n, btn in enumerate(self._buttons.values()):
            if row_fill == 0:
                row_number += 1
                row_fill = self._markup[row_number]
                self.keyboard.row(*row)
                row = []

            row_fill -= 1
            if btn.text == '__':
                self._cmd_btn = btn
                continue
            if kb_type == 'inline':
                row.append(btn._get_inline())
            elif kb_type == 'reply':
                row.append(btn._get_reply())
        self.keyboard.row(*row)

    def _show(self, bot, message, kb_type, is_new, parse_mode=None):
        if kb_type == 'reply':
            self._rows_compose(types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=self.row_width), kb_type)
            return bot.send_message(message.chat.id, self.message_text, reply_markup=self.keyboard, parse_mode=parse_mode)
        elif kb_type == 'inline':
            self._rows_compose(types.InlineKeyboardMarkup(row_width=self.row_width), kb_type)
            if is_new:
                return bot.send_message(message.chat.id, self.message_text, reply_markup=self.keyboard, parse_mode=parse_mode)
            else:
                return bot.edit_message_text(self.message_text, message.chat.id, message.id, reply_markup=self.keyboard, parse_mode=parse_mode)

    def _press_btn(self, message):
        if message.text in self._buttons.keys():
            return self._buttons[message.text]._press(message)
        else:
            return self._cmd_btn._press(message)


class KeyboardManager:

    def __init__(self, bot, kb_type='reply', parse_mode=None):
        self._type = kb_type
        self._bot = bot
        self._keyboards = {}
        self._entry = None
        self._current = {}
        self._history = {}
        self._parse_mode = parse_mode

    def _msg(self, message, text):
        self._bot.send_message(message.chat.id, text, parse_mode=self._parse_mode)

    def new_keyboard(self, name: str, msg: str, rows: list, entry=False, user_input_handler=None):
        """
        Create new Keyboard for manager

        :param name: Keyboard uniq name
        :param msg: text of message, show when keyboard appears
        :param rows: list of rows: list, one row contains a Buttons
        :param entry: mark Keyboard as entry point for manager
        :param user_input_handler: Button or Button command
        """
        self._keyboards[name] = Keyboard(msg, rows, user_input_handler=user_input_handler)
        if entry:
            self._entry = name

    def add_keyboard(self, name: str, keyboard: Keyboard, entry=False):
        """
        add an existing Keyboard to manager

        :param name: Keyboard uniq name
        :param keyboard: Keyboard obj
        :param entry: mark Keyboard as entry point for manager
        """
        self._keyboards[name] = keyboard
        if entry:
            self._entry = name

    def add_many(self, collection: dict):
        """
        add an existing Keyboards dict to manager

        :param collection: {name: Keyboard}
        """
        for name, kb in collection.items():
            self.new_keyboard(name, *kb)

    def set_entry(self, name: str):
        """
        Set Keyboard as entry point for manager

        :param name: Keyboard name
        """
        self._entry = name

    def start(self, message: types.Message):
        """
        Highly recommends to use KeyboardAdministrator cls
        starts the KeyboardsManager

        :param message:
        """
        if not self._entry:
            raise KeyError('No Entry Point')
        self._history[message.chat.id] = []
        return self._change_worker(message, self._entry, True)

    def send_to(self, chat_id):
        """
        Highly recommends to use KeyboardAdministrator cls
        sends KeyboardsManager to another chat

        :param chat_id:
        """
        if not self._entry:
            raise KeyError('No Entry Point')
        fake_chat = types.Chat(chat_id, 'private')
        fake_message = types.Message(None, None, None, fake_chat, None, [], None)
        self._history[fake_message.chat.id] = []
        return self._change_worker(fake_message, self._entry, True)

    def _change_worker(self, message, name: str, new_message=False):
        if message.chat.id in self._current.keys():
            if self._current[message.chat.id]:
                self._history[message.chat.id].append(self._current[message.chat.id])
        self._current[message.chat.id] = name
        return self._keyboards[self._current[message.chat.id]]._show(self._bot, message, self._type, new_message, parse_mode=self._parse_mode)

    def _back(self, message):
        if self._current[message.chat.id] == self._entry:
            self._history[message.chat.id] = [self._entry]
        self._current[message.chat.id] = None
        self._change_worker(message, self._history[message.chat.id].pop())

    def reply(self, message: Union[types.Message, types.CallbackQuery]):
        """
        Highly recommends to use KeyboardAdministrator cls
        reply to button press
        """
        if type(message) is types.CallbackQuery:
            message.message.text = message.data
            message = message.message
        if message.chat.id not in self._current.keys():
            return self.start(message)
        response = self._keyboards[self._current[message.chat.id]]._press_btn(message)
        if response is None:
            return
        for command in response.split(':>>'):
            if ':goto>>' in command:
                if command.split('>>')[1] in self._keyboards.keys():
                    self._change_worker(message, command.split('>>')[1])
            elif command == ':back:':
                self._back(message)
            elif command == ':home:':
                self.start(message)
            elif ':msg>>' in command:
                self._msg(message, command.split('>>')[1])
            else:
                print(f'Ignored {command = } from command string \'{response}\'')


class _MultiLineAdmin:

    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_MultiLineAdmin, cls).__new__(cls)
        return cls._instance

    def __init__(self, bot):
        if not self._inited:
            self._bot = bot
            self._managers = {}
            self._inited = True

    def add(self, message, manager):
        if message.chat.id not in self._managers.keys():
            self._managers[message.chat.id] = {}
        self._managers[message.chat.id][manager.start(message).id] = manager

    def add_to(self, chat_id, manager):
        if chat_id not in self._managers.keys():
            self._managers[chat_id] = {}
        self._managers[chat_id][manager.send_to(chat_id).id] = manager

    def reply(self, call):
        try:
            self._managers[call.message.chat.id][call.message.id].reply(call)
        except KeyError:
            self._bot.send_message(call.message.chat.id, _error_message)


class _ReplyAdmin:

    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_ReplyAdmin, cls).__new__(cls)
        return cls._instance

    def __init__(self, bot):
        if not self._inited:
            self._active_manager = {}
            self._bot = bot
            self._inited = True

    def start(self, message, manager):
        self._active_manager[message.chat.id] = manager
        self._active_manager[message.chat.id].start(message)

    def reply(self, message):
        if message.chat.id not in self._active_manager.keys():
            self._bot.send_message(message.chat.id, _error_message)
        else:
            self._active_manager[message.chat.id].reply(message)


class KeyboardAdministrator:

    _instance = None
    _inited = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeyboardAdministrator, cls).__new__(cls)
        return cls._instance

    def __init__(self, bot: TeleBot):
        if not KeyboardAdministrator._inited:
            self.handler = _EventHandler()
            self._reply_admin = _ReplyAdmin(bot)
            self._ml_admin = _MultiLineAdmin(bot)
            self._bot = bot
            KeyboardAdministrator._inited = True

    def add_inline(self, message, il_manager):
        self._ml_admin.add(message, il_manager)

    def add_inline_to(self, chat_id, il_manager):
        self._ml_admin.add_to(chat_id, il_manager)

    def start(self, message, re_manager):
        self._reply_admin.start(message, re_manager)

    def reply(self, data):
        if type(data) is types.CallbackQuery:
            self._ml_admin.reply(data)
        elif type(data) is types.Message:
            self._reply_admin.reply(data)
