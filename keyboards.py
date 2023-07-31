from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Room
from sqlalchemy import create_engine, and_

engine = create_engine('sqlite+pysqlite:///schedule.db', echo=True)

def initial_keyboard():
    initial_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, row_width=2, one_time_keyboard=True)
    initial_buttons = [KeyboardButton(text="Venue booking"), KeyboardButton(text="Cancel booking")]
    initial_keyboard.add(*initial_buttons)
    return initial_keyboard

def create_date_keyboard():
    dates = [date.today() + timedelta(days=i) for i in range(4)]
    date_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, row_width=2, one_time_keyboard=True)
    date_buttons = [KeyboardButton(text=f"{date.strftime('%a')} {date.strftime('%d/%m')}") for date in dates]
    date_keyboard.add(*date_buttons)
    return date_keyboard

def create_lounge_keyboard():
    lounges = ["12L Lounge", "13L Lounge", "14L Lounge", "12L Study Room"]
    lounge_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, row_width=2, one_time_keyboard=True)
    lounge_buttons = [KeyboardButton(text=lounge) for lounge in lounges]
    lounge_keyboard.add(*lounge_buttons)
    return lounge_keyboard

def create_time_keyboard(date, lounge):
    with Session(engine) as session:
        stmt = select(Room).where(and_(Room.location == lounge, Room.date == date))
        result = session.scalar(stmt)
        if result == None:
            newBooking = Room(location=lounge, date=date)
            session.add(newBooking)
            session.commit()
            time_slots = [f"{hour:02d}:00" for hour in range(24)]
            time_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, row_width=4, one_time_keyboard=True)
            time_buttons =[]
            for time_slot in time_slots:
                time_buttons.append(KeyboardButton(text=time_slot + ": Available"))
            time_keyboard.add(*time_buttons)
            return time_keyboard
        else:
            time_slots = result.time_slots
            time_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, row_width=4, one_time_keyboard=True)
            time_buttons = []
            for time_slot in time_slots:
                if getattr(result, time_slot) == None or getattr(result, time_slot) == "Available":
                    time_buttons.append(KeyboardButton(text=time_slot + ": Available"))
                else:
                    time_buttons.append(KeyboardButton(text=time_slot + ": " + getattr(result, time_slot)))
            time_keyboard.add(*time_buttons)
            return time_keyboard 

def create_cancel_keyboard(user, selected_date, selected_lounge):
    with Session(engine) as session:
        stmt = select(Room).where(and_(Room.location == selected_lounge, Room.date == selected_date))
        result = session.scalar(stmt)
        cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=False, one_time_keyboard=True)
        cancel_buttons = []
        if result == None:
            no_booking = KeyboardButton(text="No bookings, try again")
            cancel_buttons.append(no_booking)
            cancel_keyboard.add(*cancel_buttons)
            return cancel_keyboard
        time_slots = result.time_slots
        for time_slot in time_slots:
            if getattr(result, time_slot) == user:
                cancel_buttons.append(KeyboardButton(text=time_slot))
        if len(cancel_buttons) == 0:
            no_booking = KeyboardButton(text="No bookings, try again")
            cancel_buttons.append(no_booking)
        cancel_keyboard.add(*cancel_buttons)
        return cancel_keyboard

def update_booking(user, selected_date, selected_lounge, selected_time_slot):
    with Session(engine) as session:
        stmt = select(Room).where(and_(Room.location == selected_lounge, Room.date == selected_date))
        result = session.scalar(stmt)
        setattr(result, selected_time_slot, user)
        session.commit()
        return
    
def delete_booking(user, selected_date, selected_lounge, selected_time_slot):
    with Session(engine) as session:
        stmt = select(Room).where(and_(Room.location == selected_lounge, Room.date == selected_date, getattr(Room, selected_time_slot) == user))
        result = session.scalar(stmt)
        setattr(result, selected_time_slot, None)
        session.commit()
        return

        
            
        
    
