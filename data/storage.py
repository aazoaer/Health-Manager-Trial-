import datetime
import json
from data import database
from core import event_bus
from data.defaults import get_default_user_data

_INTENSITY_MIGRATION = {
    "almost no exercise": "sedentary",
    "light activity": "light_active",
    "moderate activity": "moderately_active",
    "high activity": "very_active",
    "extra active": "extra_active",
}

_ENVIRONMENT_MIGRATION = {
    "air conditioning": "ac_env",
    "cold": "cold_env",
    "hot": "hot_env",
}

def _migrate_field(value: str, migration_map: dict) -> str:
    
    if not value:
        return value
    for old_key, new_value in migration_map.items():
        if old_key in value:
            return new_value
    return value

def load_user_data() -> dict:
    
    db_data = database.get_all_data()
    defaults = get_default_user_data()
    defaults.update(db_data)
    

    if intensity := defaults.get("exercise_intensity", ""):
        defaults["exercise_intensity"] = _migrate_field(intensity, _INTENSITY_MIGRATION)
    
    if env := defaults.get("environment", ""):
        defaults["environment"] = _migrate_field(env, _ENVIRONMENT_MIGRATION)

    return defaults

def save_user_data(data: dict, update_history: bool = False) -> bool:
    
    try:
        database.save_multiple_keys(data)
        event_bus.publish(event_bus.USER_DATA_SAVED, data)
        
        if update_history:
            try:
                update_today_summary()
            except Exception as e:
                print(f"Error updating summary: {e}")

        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_all_history() -> dict:
    
    if not database._db_initialized:
        database.init_db()
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    history = {}
    cursor.execute("SELECT date, summary FROM history")
    for row in cursor.fetchall():
        try:
            history[row['date']] = json.loads(row['summary'])
        except json.JSONDecodeError:
            pass
    
    conn.close()
    return history

def save_all_history(data: dict) -> bool:
    
    try:
        for date_str, summary in data.items():
            database.save_history(date_str, summary)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def save_daily_summary(date_str: str, summary: dict) -> None:
    
    database.save_history(date_str, summary)

def load_daily_summary(date_str: str) -> dict:
    
    return database.get_daily_history(date_str)

def load_month_summaries(year: int, month: int) -> dict:
    
    return database.get_month_history(year, month)

def update_today_summary() -> dict:
    
    from core.calculations import (
        calculate_water_goal, calculate_nutrition_goals,
        calculate_nutrition_score, calculate_sleep_score, calculate_exercise_score
    )
    
    user_data = load_user_data()
    today = datetime.date.today().isoformat()
    

    water_intake = user_data.get("water_intake", 0)
    water_goal = calculate_water_goal(user_data)
    water_achieved = water_intake >= water_goal
    

    actual_intake = _calculate_actual_intake(user_data, today)
    nutrition_goals = calculate_nutrition_goals(user_data)
    nutrition_score = calculate_nutrition_score(actual_intake, nutrition_goals)
    

    sleep_duration, sleep_grade = _calculate_sleep_data(user_data, today, calculate_sleep_score)
    

    exercise_duration, exercise_calories, exercise_score = _calculate_exercise_data(
        user_data, today, calculate_exercise_score
    )
    
    summary = {
        "water_intake": water_intake,
        "water_goal": water_goal,
        "water_achieved": water_achieved,
        "nutrition_score": nutrition_score,
        "sleep_grade": sleep_grade,
        "sleep_duration": sleep_duration,
        "exercise_score": exercise_score,
        "exercise_duration": exercise_duration,
        "exercise_calories": exercise_calories
    }
    
    save_daily_summary(today, summary)
    return summary

def _calculate_actual_intake(user_data: dict, today: str) -> dict:
    
    actual_intake = {}
    daily_meals = user_data.get("daily_meals", {})
    
    if daily_meals.get("date") == today:
        for meal in daily_meals.get("meals", []):
            level1 = meal.get("level1", {})
            for key, value in level1.items():
                if isinstance(value, (int, float)):
                    actual_intake[key] = actual_intake.get(key, 0) + value
    
    return actual_intake

def _calculate_sleep_data(user_data: dict, today: str, score_func) -> tuple:
    
    daily_sleep = user_data.get("daily_sleep", {})
    
    if daily_sleep.get("date") != today:
        return 0, "F"
    
    records = daily_sleep.get("records", [])
    if not records:
        return 0, "F"
    
    sleep_duration = sum(r.get("duration_minutes", 0) for r in records)
    qualities = [r.get("quality", "fair") for r in records]
    quality_order = {"excellent": 0, "good": 1, "fair": 2, "poor": 3}
    best_quality = min(qualities, key=lambda q: quality_order.get(q, 2))
    sleep_grade = score_func(sleep_duration, best_quality)
    
    return sleep_duration, sleep_grade

def _calculate_exercise_data(user_data: dict, today: str, score_func) -> tuple:
    
    daily_exercises = user_data.get("daily_exercises", {})
    
    if daily_exercises.get("date") != today:
        return 0, 0, 0
    
    records = daily_exercises.get("records", [])
    if not records:
        return 0, 0, 0
    
    exercise_duration = sum(r.get("duration_minutes", 0) for r in records)
    exercise_calories = sum(r.get("calories", 0) for r in records)
    exercise_score = score_func(records, user_data)
    
    return exercise_duration, exercise_calories, exercise_score
