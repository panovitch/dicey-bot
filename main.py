#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import os
import logging

from telegram.ext import Updater, CommandHandler
from rolling import Roll
from db import DB
from collections import defaultdict

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def escape_markdown(string):
    return string.replace('+', '\\+').replace('-', '\\-').replace('(', '\\(').replace(')', '\\)')


def roll_handler(update, context, rollstring=None):
    """Echo the user message."""
    rollstring = rollstring or " ".join(context.args)

    user_data = DB(user_id=str(update.message.from_user.id))
    saved_rolls = user_data.get_saved_rolls()

    saved_roll = None
    for saved_roll_name, saved_roll_value in saved_rolls.items():
        if saved_roll_name.lower() in rollstring.lower():
            saved_roll = Roll.from_rollstring(saved_roll_value)

    roll = saved_roll or Roll.from_rollstring(rollstring)

    username = f'*{update.message.from_user.first_name}*' if update.message.from_user.first_name else f'@{update.message.from_user.username}'
    update.message.reply_markdown_v2(
        escape_markdown(
            f"{username} rolled *{roll.result}*  \n"
            f"`{(roll.as_detailed())} = {roll.result}`")
        )

    user_data.save_previous_roll(rollstring)


def reroll_handler(update, context):
    """Echo the user message."""
    user_data = DB(user_id=str(update.message.from_user.id))
    last_roll = user_data.get_previous_roll()

    if last_roll:
        roll_handler(update, context, rollstring=last_roll)
    else:
        update.message.reply_text('No previous rolls!')


def save_roll_handler(update, context):
    label = context.args[0]
    rollstring = " ".join(context.args[1:])

    try:
        Roll.from_rollstring(rollstring)
    except Exception:
        update.message.reply_text('Invalid save format! Use /save <label> <roll>.')
        return

    user_data = DB(user_id=str(update.message.from_user.id))
    user_data.save_roll(label, rollstring)
    username = f'{update.message.from_user.first_name}' if update.message.from_user.first_name else f'@{update.message.from_user.username}'

    update.message.reply_text(f'Saved roll "{rollstring}" as "{label}" for {username}!')


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.environ.get('DICEY_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler(["roll", 'r'], roll_handler))
    dp.add_handler(CommandHandler(["reroll", 'rr'], reroll_handler))
    dp.add_handler(CommandHandler("save", save_roll_handler))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
