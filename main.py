import os
import telebot
from dotenv import load_dotenv
from keyboards import create_date_keyboard, create_time_keyboard, create_lounge_keyboard, initial_keyboard, create_cancel_keyboard
from keyboards import update_booking, delete_booking

load_dotenv()

BOT_TOKEN = os.environ.get('API_KEY')
bot = telebot.TeleBot(BOT_TOKEN)
user_data = {}

def is_valid_date(message):
    dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    try:
        lis = message.text.split()
        if len(lis) != 2:
            return False
        if lis[0] not in dates:
            return False
        tmp = lis[1].split('/')
        try:
            day = int(tmp[0])
            month = int(tmp[1])
            if int(day <= 31 and day >= 1 and month <= 12 and month >= 1):
                return True
        except ValueError:
            return False
        return True
    except ValueError:
        return False 
    
def is_valid_lounge(message):
    lounges = ["12L Lounge", "13L Lounge", "14L Lounge", "12L Study Room"]
    try:
        tmp = message.text
        if tmp not in lounges:
            return False
        return True
    except ValueError:
        return False
    
def is_valid_time(message):
    try:
        tmp = message.text.split(':')
        hour = int(tmp[0])
        minute = int(tmp[1])
        if int(hour <= 23 and hour >= 0 and minute <= 59 and minute >= 0):
            return True
        return False
    except ValueError:
        return False
    
def is_cancel_booking(message):
    try:
        tmp = message.text
        if tmp == "Cancel booking":
            return True
        return False
    except ValueError:
        return False
    
def is_lounge_booking(message):
    try:
        tmp = message.text
        if tmp == "Venue booking":
            return True
        return False
    except ValueError:
        return False
    
def is_no_booking(message):
    try:
        tmp = message.text
        if tmp == "No bookings, try again":
            return True
        return False
    except ValueError:
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username
    user_data[username] = {}
    bot.reply_to(message, "Welcome to the Phoenix Bot! Please select a option below:", reply_markup=initial_keyboard())
    
@bot.message_handler(func=is_lounge_booking)
def handle_lounge_booking(message):
    selected_option = message.text
    username = message.from_user.username
    user_data[username]['option'] = selected_option
    print(user_data)
    bot.reply_to(message, "Please select a date for your booking.", reply_markup=create_date_keyboard())
    
@bot.message_handler(func=is_cancel_booking)
def handle_cancel_booking(message):
    selected_option = message.text
    username = message.from_user.username
    user_data[username]['option'] = selected_option
    print(user_data)
    bot.reply_to(message, "Please select a date to cancel your booking.", reply_markup=create_date_keyboard())
    
@bot.message_handler(func=is_valid_date)
def handle_date(message):
    selected_date = message.text
    user_data[message.from_user.username]['date'] = selected_date
    print(user_data)
    bot.reply_to(message, f"Great! You have selected {selected_date}. Now, please select the location.", reply_markup=create_lounge_keyboard())
    
@bot.message_handler(func=is_valid_lounge)
def handle_lounge(message):
    username = message.from_user.username
    selected_lounge = message.text
    selected_date = user_data[username]['date']
    user_data[username]['lounge'] = selected_lounge
    print(user_data)
    if user_data[username]['option'] == "Cancel booking":
        bot.reply_to(message, f"Great! You have selected {selected_lounge}. Now, please select booking you want to cancel.", reply_markup=create_cancel_keyboard(username, selected_date, selected_lounge))
    else:
        bot.reply_to(message, f"Great! You have selected {selected_lounge}. Now, please select the time for your booking.", reply_markup=create_time_keyboard(selected_date, selected_lounge))
    
@bot.message_handler(func=is_no_booking)
def handle_no_bookings(message):
    bot.reply_to(message, "No bookings, try again", reply_markup=create_date_keyboard())

@bot.message_handler(func=is_valid_time)
def handle_time(message):
    selected_time = message.text
    username = message.from_user.username
    selected_option = user_data[username]['option']
    selected_date = user_data[username]['date']
    selected_lounge = user_data[username]['lounge']
    if selected_option == "Cancel booking":
        delete_booking(username, selected_date, selected_lounge, selected_time)
        bot.reply_to(message, f"Your booking for {selected_lounge} on {selected_date} at {selected_time} has been cancelled!")
        if username in user_data:
            del user_data[username]
        return
    # check if already booked
    tmp = selected_time.split(": ")
    if tmp[1] == "Available":
        selected_time = tmp[0]
    else:
        bot.reply_to(message, "This time slot is already taken, please try again.", reply_markup=create_time_keyboard(user_data[message.from_user.username]['date'], user_data[message.from_user.username]['lounge']))
        return
    update_booking(username, selected_date, selected_lounge, selected_time)
    bot.reply_to(message, f"Your booking for {selected_lounge} on {selected_date} at {selected_time} has been confirmed!")
    # Clear user_data for this user after the booking is confirmed
    if username in user_data:
        del user_data[username]
        
#TODO: Add a command to view bookings

# handle everything else thats not a command
@bot.message_handler(func=lambda message: True)
def handle_invalid_command(message):
    bot.reply_to(message, "Invalid command. Please try again.")
    
bot.infinity_polling()