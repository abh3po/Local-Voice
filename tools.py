# tools.py
import threading
import time
import re


def stop_listening_tool(state):
    print("Action called")
    state["mic_enabled"] = False
    state["wake_only_mode"] = True
    return "Stopped listening. Say 'start listening' to resume."


def start_listening_tool(state, play_sound_fn, sound_file):
    print("Action called")
    state["mic_enabled"] = True
    state["wake_only_mode"] = False
    threading.Thread(target=play_sound_fn, args=(
        sound_file,), daemon=True).start()
    return "Listening resumed."


def set_timer_tool(duration: str, message: str = "Time is up!") -> str:
    print("Action called, set_timer", duration, message)
    try:
        # parse duration string
        pattern = r'(\d+)\s*(s|sec|seconds?|m|min|minutes?|h|hr|hours?)'
        match = re.match(pattern, duration.strip().lower())
        if not match:
            return "I couldn't understand the duration."

        value, unit = match.groups()
        value = int(value)
        seconds = 0
        if unit.startswith('s'):
            seconds = value
        elif unit.startswith('m'):
            seconds = value * 60
        elif unit.startswith('h'):
            seconds = value * 3600

        def timer_thread():
            time.sleep(seconds)
            play_response(f"Timer done: {message}")

        threading.Thread(target=timer_thread, daemon=True).start()
        return f"Timer set for {duration}."
    except Exception as e:
        return "An Error occured in setting the timer " + str(e)
