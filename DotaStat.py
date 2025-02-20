import json
import requests
import matplotlib.pyplot as plt
from tkinter import Tk, Entry, Button, Label

# Загружаем имена героев
with open('hero_ids.json', 'r') as file:
    hero_names_data = json.load(file)
hero_names_dict = {hero['id']: hero['name'] for hero in hero_names_data['result']['heroes']}


def fetch_match_data():
    match_id = entry.get()
    if not match_id.isdigit():
        status_label.config(text="Please enter a valid match ID.")
        return

    url = f"https://api.opendota.com/api/matches/{match_id}"
    response = requests.get(url)
    match_data = response.json()

    if 'error' in match_data:
        status_label.config(text=f"Error: {match_data['error']}")
        return

    create_kda_plot(match_data)
    status_label.config(text="Match statistics displayed.")


def fetch_player_win_lose_data():
    account_id = entry.get()
    if not account_id.isdigit():
        status_label.config(text="Please enter a valid player ID")
        return

    # Запрос для win/lose
    url_wl = f"https://api.opendota.com/api/players/{account_id}/wl"
    response_wl = requests.get(url_wl)
    win_lose_data = response_wl.json()
    if 'error' in win_lose_data:
        status_label.config(text=f"Error: {win_lose_data['error']}")
        return

    # Запрос для имени игрока
    url_player = f"https://api.opendota.com/api/players/{account_id}"
    response_player = requests.get(url_player)
    player_data = response_player.json()
    if 'error' in player_data:
        status_label.config(text=f"Error: {player_data['error']}")
        return

    # Получаем имя игрока
    player_name = player_data.get('profile', {}).get('personaname', 'Unknown')

    create_win_lose_bar(win_lose_data, player_name)
    status_label.config(text="Win/Lose stats displayed.")


def create_win_lose_bar(win_lose_data, player_name):
    wins = win_lose_data.get('win', 0)
    losses = win_lose_data.get('lose', 0)

    categories = ['Wins', 'Losses']
    values = [wins, losses]
    colors = ['green', 'red']

    plt.figure(figsize=(6, 4))
    plt.bar(categories, values, color=colors)

    plt.title(f"Player Win/Loss Record: {player_name}")
    plt.ylabel("Count")
    for i, value in enumerate(values):
        plt.text(i, value + 0.5, str(value), ha='center')
    plt.show()


def create_kda_plot(match_data):
    def calculate_kda(kills, deaths, assists):
        return (kills + assists) / max(deaths, 1)

    fig, axes = plt.subplots(5, 2, figsize=(20, 30))
    fig.suptitle('KDA for First 10 Players', fontsize=16)
    axes = axes.ravel()

    for i, player in enumerate(match_data.get('players', [])[:10]):
        hero_id = player.get('hero_id')
        hero_name = hero_names_dict.get(hero_id, f"Unknown Hero ID {hero_id}")

        kills = player.get('kills', 0)
        deaths = player.get('deaths', 0)
        assists = player.get('assists', 0)

        kda = calculate_kda(kills, deaths, assists)

        x = ['Kills', 'Deaths', 'Assists']
        y = [kills, deaths, assists]
        axes[i].bar(x, y, color=['#ff9999', '#66b3ff', '#99ff99'])
        axes[i].set_title(f'KDA for {hero_name}: {kda:.2f}')
        axes[i].set_ylabel('Count')
        axes[i].text(0.5, max(y) * 1.1, f'KDA: {kda:.2f}', horizontalalignment='center')

    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    plt.show()


# GUI
root = Tk()
root.title("Match Statistics Viewer")

entry = Entry(root, width=50)
entry.pack()


def paste(event):
    try:
        entry.event_generate('<<Paste>>')
    except:
        pass


entry.bind("<Button-3>", paste)

Button(root, text="Get Match Stats", command=fetch_match_data).pack()
Button(root, text="Get Player Win/Lose", command=fetch_player_win_lose_data).pack()

status_label = Label(root, text="")
status_label.pack()

instructions = Label(root, text="Right-click to paste match or player ID")
instructions.pack()

root.mainloop()
