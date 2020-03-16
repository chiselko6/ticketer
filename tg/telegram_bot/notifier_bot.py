from datetime import datetime, timedelta
from functools import partial
from structlog import get_logger
from typing import Any, MutableMapping, Optional, TypeVar
from urllib.parse import urljoin
import re
import requests

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from calendar_telegram import telegramcalendar

from . import settings
from .constants import (
    CALENDAR_NEXT_DAYS_INTERVAL,
    CURRENT_CHOICE_TYPE,
    DATE_CHOICE,
    DESTINATION_CHOICE,
    FULFIL_STATE,
    LANGUAGE_CHOICE,
    MIN_SEATS_CHOICE,
    RESET_COMMAND,
    SEARCH_CHOICE,
    SEAT_TYPE_CHOICE,
    SOURCE_CHOICE,
    START_COMMAND,
    START_OVER,
    STATE,
    STATE_CHANGES,
    TRAIN_NUM_CHOICE,
    UNDO_COMMAND,
    WAIT_FOR_INPUT,
    WAIT_JOB_RESULTS,
)

DATA_TYPE = TypeVar('DATA_TYPE', str, int)

logger = get_logger()


def caption_with_state(state: Any, caption: str) -> str:
    if state is not None:
        return f'{caption}{f" ({state})" if state else ""}'

    return caption


def get_default_state() -> MutableMapping[DATA_TYPE, Any]:
    return {
        LANGUAGE_CHOICE: 'ru',
        MIN_SEATS_CHOICE: 1,
        DATE_CHOICE: 'tomorrow',
    }


def start(update: Update, context: CallbackContext) -> DATA_TYPE:
    text = f'Enter your requisites. To abort, type /{RESET_COMMAND}. To undo last command, type /{UNDO_COMMAND}.'

    user_data = context.user_data

    if START_OVER not in user_data:
        user_data[START_OVER] = True

    if user_data[START_OVER]:
        user_data[STATE] = get_default_state()
        user_data[STATE_CHANGES] = []

    state = user_data[STATE]

    buttons = [[
        InlineKeyboardButton(text=caption_with_state(state.get(SOURCE_CHOICE), 'Source'),
                             callback_data=str(SOURCE_CHOICE)),
    ], [
        InlineKeyboardButton(text=caption_with_state(state.get(DESTINATION_CHOICE), 'Destination'),
                             callback_data=str(DESTINATION_CHOICE)),
    ], [
        InlineKeyboardButton(text=caption_with_state(state.get(DATE_CHOICE), 'Date'),
                             callback_data=str(DATE_CHOICE)),
    ], [
        InlineKeyboardButton(text=caption_with_state(state.get(MIN_SEATS_CHOICE), 'Min seats'),
                             callback_data=str(MIN_SEATS_CHOICE)),
        InlineKeyboardButton(text=caption_with_state(state.get(TRAIN_NUM_CHOICE), 'Train num'),
                             callback_data=str(TRAIN_NUM_CHOICE)),
    ], [
        InlineKeyboardButton(text=caption_with_state(state.get(SEAT_TYPE_CHOICE), 'Seat type'),
                             callback_data=str(SEAT_TYPE_CHOICE)),
        InlineKeyboardButton(text=caption_with_state(state.get(LANGUAGE_CHOICE), 'Language'),
                             callback_data=str(LANGUAGE_CHOICE)),
    ], [
        InlineKeyboardButton(text='Search', callback_data=SEARCH_CHOICE),
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    if update.callback_query is not None:
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    user_data[START_OVER] = False

    return FULFIL_STATE


def ask_for_input(update: Update, context: CallbackContext, *, prompt: str) -> DATA_TYPE:
    context.user_data[CURRENT_CHOICE_TYPE] = update.callback_query.data

    update.callback_query.edit_message_text(text=prompt)

    return WAIT_FOR_INPUT


def ask_calendar_input(update: Update, context: CallbackContext) -> DATA_TYPE:
    context.user_data[CURRENT_CHOICE_TYPE] = update.callback_query.data

    keyboard = telegramcalendar.create_calendar(
        from_date=datetime.now(),
        to_date=datetime.now() + timedelta(days=CALENDAR_NEXT_DAYS_INTERVAL),
    )

    update.callback_query.edit_message_text(text='Travelling date:',
                                            reply_markup=keyboard)

    return WAIT_FOR_INPUT


def save_input(update: Update, context: CallbackContext) -> Optional[DATA_TYPE]:
    user_data = context.user_data

    if user_data[CURRENT_CHOICE_TYPE] == DATE_CHOICE:
        update.callback_query.answer('Got it')
        was_selected, selected_date = telegramcalendar.process_calendar_selection(
            context.bot,
            update,
            from_date=datetime.now(),
            to_date=datetime.now() + timedelta(days=CALENDAR_NEXT_DAYS_INTERVAL),
        )

        if was_selected:
            user_input = selected_date.strftime("%Y-%m-%d")
        else:
            return None

    else:
        user_input = update.message.text

        if user_data[CURRENT_CHOICE_TYPE] == MIN_SEATS_CHOICE:
            try:
                user_input = int(user_input)
            except ValueError:
                update.message.reply_text(text='Minimum seats must be integer. Please try again')

                logger.debug('min_seats.invalid', value=user_input)

                return start(update, context)

        elif user_data[CURRENT_CHOICE_TYPE] == LANGUAGE_CHOICE:
            if user_input not in ('ru', 'en'):
                update.message.reply_text(text='Only `ru` and `en` choices are currently supported for language.',
                                          parse_mode=ParseMode.MARKDOWN)

                logger.debug('language.invalid', value=user_input)

                return start(update, context)

        else:
            user_input = user_input.capitalize()

    prev_value = user_data[STATE].get(user_data[CURRENT_CHOICE_TYPE])
    user_data[STATE][user_data[CURRENT_CHOICE_TYPE]] = user_input
    user_data[STATE_CHANGES].append((user_data[CURRENT_CHOICE_TYPE], prev_value, user_input))

    return start(update, context)


def stop(update: Update, context: CallbackContext) -> DATA_TYPE:
    update.message.reply_text(f'All cleared, you can start from scratch (/{START_COMMAND})')

    context.user_data[START_OVER] = True

    return start(update, context)


def undo_input(update: Update, context: CallbackContext) -> DATA_TYPE:
    user_data = context.user_data
    user_changes = user_data[STATE_CHANGES]

    if not user_changes:
        update.message.reply_text('No changes made')
    else:
        last_change_type, prev_value, _ = user_changes.pop()
        user_data[STATE][last_change_type] = prev_value

    return start(update, context)


def search(update: Update, context: CallbackContext) -> DATA_TYPE:
    user_data = context.user_data

    if user_data[STATE].get(SOURCE_CHOICE) \
       and user_data[STATE].get(DESTINATION_CHOICE) \
       and user_data[STATE].get(DATE_CHOICE):

        update.callback_query.answer(text='Starting...')

        user_input = {
            'crawler_src': user_data[STATE][SOURCE_CHOICE],
            'crawler_dest': user_data[STATE][DESTINATION_CHOICE],
            'crawler_date': user_data[STATE][DATE_CHOICE],
            'crawler_min_seats': user_data[STATE][MIN_SEATS_CHOICE],
            'crawler_train_num': user_data[STATE].get(TRAIN_NUM_CHOICE),
            'crawler_seat_type': user_data[STATE].get(SEAT_TYPE_CHOICE),
            'crawler_lang': user_data[STATE][LANGUAGE_CHOICE],
        }

        url = urljoin(settings.FINDER_HOST, '/find/rw')
        response = requests.post(url, json={
            'tg_bot_token': settings.TG_TOKEN,
            'tg_chat_id': update.effective_chat.id,
            **user_input,
        })

        bot = context.bot

        if response.ok:
            data = response.json()
            job_id = data['job_id']

            buttons = [[
                InlineKeyboardButton(text='Check status',
                                     callback_data=f'Check: {str(job_id)}'),
            ], [
                InlineKeyboardButton(text='Cancel', callback_data=f'Cancel: {str(job_id)}')
            ]]
            keyboard = InlineKeyboardMarkup(buttons)

            bot.send_message(update.callback_query.message.chat_id,
                             text='We started searching!', reply_markup=keyboard)

            logger.info('search.ok', **user_input)

            return WAIT_JOB_RESULTS
        else:
            update.callback_query.answer(':(')
            bot.send_message(update.callback_query.message.chat_id,
                             text='Sorry, something went wrong. You can try again')

            logger.error('search.failed', reason=response.text, status_code=response.status_code)

            return start(update, context)

    else:
        update.callback_query.answer(text='You have unfilled data')

        return FULFIL_STATE


def check_status(update: Update, context: CallbackContext) -> Optional[DATA_TYPE]:
    match = re.match('^Check: (?P<job_id>.+)$', update.callback_query.data)
    job_id = match.groupdict()['job_id']

    url = urljoin(settings.FINDER_HOST, f'/check_state/{job_id}')
    response = requests.get(url)
    if response.ok:
        if response.text == 'failed':
            update.callback_query.answer(text='Your job failed')
            return start(update, context)

        elif response.text in ('started', 'queued', 'deferred', 'scheduled'):
            update.callback_query.answer(text='Your job is in progress.')
            return None

        elif response.text == 'finished':
            update.callback_query.edit_message_text('Your job has finished. You should have received the results.')
            return None

    logger.warning('check_status.failed', reason=response.text, status_code=response.status_code)

    update.callback_query.answer("Couldn't retrieve the status.")

    return None


def cancel_job(update: Update, context: CallbackContext) -> Optional[DATA_TYPE]:
    match = re.match('^Cancel: (?P<job_id>.+)$', update.callback_query.data)
    job_id = match.groupdict()['job_id']

    url = urljoin(settings.FINDER_HOST, f'/cancel/')
    response = requests.post(url, json={'job_id': job_id})

    if response.ok:
        update.callback_query.answer('👍')
        update.callback_query.edit_message_text(text='Your job is cancelled')
        return ConversationHandler.END

    else:
        update.callback_query.answer("Couldn't cancel your job")

        logger.warning('cancel_job.failed', reason=response.text, status_code=response.status_code)

        return None


def run_bot():
    updater = Updater(settings.TG_TOKEN, use_context=True)

    dp = updater.dispatcher

    req_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(START_COMMAND, start)],
        states={
            FULFIL_STATE: [
                CallbackQueryHandler(partial(ask_for_input, prompt='Choose your source:'),
                                     pattern=f'^{SOURCE_CHOICE}$'),
                CallbackQueryHandler(partial(ask_for_input, prompt='Choose your destination:'),
                                     pattern=f'^{DESTINATION_CHOICE}$'),
                CallbackQueryHandler(ask_calendar_input, pattern=f'^{DATE_CHOICE}$'),
                CallbackQueryHandler(partial(ask_for_input, prompt='Minimum seats:'),
                                     pattern=f'^{MIN_SEATS_CHOICE}$'),
                CallbackQueryHandler(partial(ask_for_input, prompt='Train number:'),
                                     pattern=f'^{TRAIN_NUM_CHOICE}$'),
                CallbackQueryHandler(partial(ask_for_input, prompt='Seat type:'),
                                     pattern=f'^{SEAT_TYPE_CHOICE}$'),
                CallbackQueryHandler(partial(ask_for_input, prompt='Language:'),
                                     pattern=f'^{LANGUAGE_CHOICE}$'),

                CallbackQueryHandler(search, pattern=f'^{SEARCH_CHOICE}$'),

                CommandHandler(UNDO_COMMAND, undo_input),
            ],

            WAIT_JOB_RESULTS: [
                CallbackQueryHandler(check_status, pattern='^Check: .+$'),
                CallbackQueryHandler(cancel_job, pattern='^Cancel: .+$'),
            ],

            WAIT_FOR_INPUT: [
                MessageHandler(Filters.text, save_input),
                CallbackQueryHandler(save_input),  # no pattern due to complex choice
            ],

        },
        fallbacks=[
            CommandHandler(RESET_COMMAND, stop),
            CommandHandler(START_COMMAND, start),
        ],
    )

    dp.add_handler(req_conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    run_bot()
