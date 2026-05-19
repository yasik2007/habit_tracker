import json
from datetime import datetime
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import asyncio
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

DATA_FILE = "habits.json"

# JSON helpers

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# /start

@dp.message(Command("start"))
async def start(message: Message):
    text = (
        "Hi;)\n\n"
        "I am your habit tracker bot\n\n"
        "Commands:\n"
        "/commands\n"
        "/add <habit>\n"
        "/list\n"
        "/done <habit>\n"
        "/delete <habit>\n"
        "/today\n"
        "/graph\n"
        "/stats\n"
        "/motivation"
    )

    await message.answer(text)

# /commands

@dp.message(Command("commands"))
async def commands(message: Message):
    text = (
        "Сommands:\n\n"
        "/commands\n"
        "/add <habit> - Add a new habit\n"
        "/list - Show all habits\n"
        "/done <habit> - Mark habit as completed today\n"
        "/delete <habit> - Delete a habit\n"
        "/today - Show today's progress\n"
        "/stats - Show statistics\n"
        "/motivation - Give you some motivation"
    )

    await message.answer(text)

# /add

@dp.message(Command("add"))
async def add_habit(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    habit_name = message.text.replace("/add", "").strip()

    if not habit_name:
        await message.answer("Please enter a habit name")
        return

    if user_id not in data:
        data[user_id] = {}

    if habit_name in data[user_id]:
        await message.answer("This habit already exists")
        return

    data[user_id][habit_name] = []

    save_data(data)

    await message.answer(f"Habit '{habit_name}' added")


# /delete

@dp.message(Command("delete"))
async def delete_habit(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    habit_name = message.text.replace("/delete", "").strip()

    if not habit_name:
        await message.answer("Please enter a habit to delete")
        return

    if user_id not in data or habit_name not in data[user_id]:
        await message.answer("Habit not found")
        return

    del data[user_id][habit_name]

    save_data(data)

    await message.answer(f" Habit '{habit_name}' deleted")


# /list

@dp.message(Command("list"))
async def list_habits(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    if user_id not in data or not data[user_id]:
        await message.answer("You have no habits yet")
        return

    text = "Your habits:\n\n"

    for habit in data[user_id]:
        text += f"• {habit}\n"

    await message.answer(text)

# /graph

@dp.message(Command("graph"))
async def graph_stats(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    if user_id not in data or not data[user_id]:
        await message.answer("No data yet")
        return

    habits = []
    counts = []

    for habit, dates in data[user_id].items():
        habits.append(habit)
        counts.append(len(dates))

    # Create graph
    plt.figure(figsize=(8, 5))
    plt.bar(habits, counts)

    plt.xlabel("Habits")
    plt.ylabel("Completions")
    plt.title("Habit Statistics")

    # Save image
    filename = f"{user_id}_stats.png"
    plt.savefig(filename)

    plt.close()

    # Send image
    photo = types.FSInputFile(filename)

    await message.answer_photo(photo)


# /done

@dp.message(Command("done"))
async def done_habit(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    habit_name = message.text.replace("/done", "").strip()

    if user_id not in data or habit_name not in data[user_id]:
        await message.answer("Habit not found")
        return

    today = datetime.now().strftime("%Y-%m-%d")

    if today in data[user_id][habit_name]:
        await message.answer("Already completed today")
        return

    data[user_id][habit_name].append(today)

    save_data(data)

    await message.answer(f"Habit '{habit_name}' completed!")

# /today

@dp.message(Command("today"))
async def today(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    if user_id not in data or not data[user_id]:
        await message.answer("No habits yet")
        return

    today_date = datetime.now().strftime("%Y-%m-%d")

    completed = []
    not_completed = []

    for habit, dates in data[user_id].items():

        if today_date in dates:
            completed.append(habit)
        else:
            not_completed.append(habit)

    text = "Today's habits\n\n"

    text += "Completed:\n"

    if completed:
        for habit in completed:
            text += f"• {habit}\n"
    else:
        text += "None\n"

    text += "\nNot completed:\n"

    if not_completed:
        for habit in not_completed:
            text += f"• {habit}\n"
    else:
        text += "None\n"

    await message.answer(text)

# /stats

@dp.message(Command("stats"))
async def stats(message: Message):
    data = load_data()

    user_id = str(message.from_user.id)

    if user_id not in data or not data[user_id]:
        await message.answer("No data yet")
        return

    date_stats = {}

    # Collect statistics
    for habit, dates in data[user_id].items():

        for date in dates:

            if date not in date_stats:
                date_stats[date] = []

            date_stats[date].append(habit)

    # Sort dates
    sorted_dates = sorted(date_stats.keys())

    text = "Full statistics:\n\n"

    for date in sorted_dates:

        habits = date_stats[date]

        text += (
            f"{date} — {len(habits)} habits completed\n"
        )

        for habit in habits:
            text += f"• {habit}\n"

        text += "\n"

    await message.answer(text)

# /motivation

@dp.message(Command("motivation"))
async def motivation(message: Message):
    await message.answer("https://www.youtube.com/watch?v=jDavfYnSJOo")

# Run bot

async def main():
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())