from config import FIELD_HEIGHT, FIELD_WIDTH
import curses as crs
from game import Game
from texts import MAIN_MENU, INSTRUCTIONS, AUTHOR_INFO, ASCII_TITLE


def main_menu(stdscr) -> str:
    current_row = 0
    while True:
        crs.start_color()
        crs.init_pair(6, crs.COLOR_RED, crs.COLOR_BLACK)
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if height < (FIELD_HEIGHT + 16) or width < FIELD_WIDTH:
            stdscr.addstr(0, 0, "Увеличьте размер окна терминала.")
            stdscr.refresh()
            stdscr.getch()
            continue

        lines = ASCII_TITLE.split("\n")
        start_y = height // 2 - len(lines)
        start_x = width // 2 - (len(lines[1]) // 2)

        for i, line in enumerate(lines):
            stdscr.addstr(start_y + i, start_x, line)

        for idx, row in enumerate(MAIN_MENU):
            x = (width // 2) - (len(row) // 2)
            y = height // 2 - len(MAIN_MENU) // 2 + idx
            if idx == current_row:
                stdscr.addstr(y, x, row, crs.color_pair(6))
            else:
                stdscr.addstr(y, x, row)

        stdscr.refresh()
        key = stdscr.getch()

        if key == 27:  # ESC
            break
        elif (key == crs.KEY_UP or key == crs.KEY_A2) and current_row > 0:
            current_row -= 1
        elif (
            (key == crs.KEY_DOWN or key == crs.KEY_C2) and
            current_row < len(MAIN_MENU) - 1
        ):
            current_row += 1
        elif key == ord('\n'):  # Enter
            if current_row == 0:
                game = Game(stdscr)
                game.play()
            elif current_row == 1:
                show_text_screen(stdscr, INSTRUCTIONS)
            elif current_row == 2:
                show_text_screen(stdscr, AUTHOR_INFO)
            elif current_row == 3:
                break


def show_text_screen(stdscr, text_list) -> None:
    stdscr.clear()
    for idx, line in enumerate(text_list):
        stdscr.addstr(FIELD_HEIGHT // 2 - len(text_list) // 2 + idx, 2, line)
    stdscr.refresh()
    stdscr.getch()


crs.wrapper(main_menu)