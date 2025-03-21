MAIN_MENU = [
    "Начать новую игру",
    "Что нужно делать",
    "Об авторе",
    "Выход"
]

INSTRUCTIONS = [
    "Цель игры: Собрать припасы и добраться до норки (O),",
    "за кратчайшее время, не попавшись злому еноту!",
    "избегая енота (R) и обломков препятствий (X).",
    "\n\nУправление:",
    "Стрелка влево/вправо - Поворот.",
    "Стрелка вверх - Идти, стрелка вниз - замедлиться",
    "Пробел - фыркнуть/отогнать енота",
    "\n\nНажмите любую клавишу, чтобы вернуться в меню."
]

ASCII_WIN = """
  Победа!
  *******
  Еж собрал все припасы!
"""

ASCII_LOSE = """
  Поражение!
  **********
  Енот украл все припасы!
"""

AUTHOR_INFO = [
    "Автор игры: Ic-0n.",
    "Мой github: https://github.com/Ic-0n011/",
    "Версия: 1.0.",
    "\nНажмите любую клавишу, чтобы вернуться в меню."
]

ASCII_TITLE = '''
▄▄████▄█████████▄▄███████████████▄███▄▄▄⌐▌
█▌  ▐██         ██         ██   "██▌  ▐█U▌
█▌  ▐██   ███▄▄▄██   ███   ██     █▌  ▐█U▌
█▌  ▐██   ████████   ███   ██   µ  ▌  ▐█U▌
█▌  ▐██   ███▀▀▀██  L███]  ██   ▌█▄   ▐█U▌
█▌  ▐██         ██         ██   ██▄▓  ▐█U▌
██▓▄▄█▀█████████▀▀█████████████████▄▄▄▐█U▌
▀▀▀█▄∞╧═^^ⁿ""""▀▀███████▄""""ⁿⁿ^══∞▄█▀▀▀─▌
                 ═▀███▌`
                   ⁿ▀
'''

# Сообщения
MSG_RACCOON_APPEAR = "Енот появился и смеётся: Ха-ха-ха!"
MSG_RACCOON_SCARED = "Енот убежал, услышав фырканье!"
MSG_RACCOON_STEAL = "Енот украл припас и исчез!"

# Звуки для звукового поля
SOUND_RACCOON = ["шорох! шорох!...", "хруст ветки..."]
SOUND_NEUTRAL = ["шшш...(звуки ветра)", "скрип...(звук деревьев)"]