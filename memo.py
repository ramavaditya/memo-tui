import curses
import json
import os
from dataclasses import dataclass
from typing import List

@dataclass
class Note:
    text: str

    def to_dict(self) -> dict:
        return {"text": self.text}

class MasonryMemoPad:
    def __init__(self, path: str = "memopad.json", columns: int | None = None) -> None:
        self.path = path
        self.columns_config = columns
        self.notes: List[Note] = []
        self.scroll = 0
        self.load()

    def load(self) -> None:
        if not os.path.exists(self.path):
            self.notes = [
                Note("Welcome to the Masonry MemoPad!"),
                Note("Press 'n' to add a new note."),
                Note("Press 's' to save your notes."),
                Note("Press 'q' to quit."),
            ]
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("notes", []) if isinstance(data, dict) else data
            self.notes = [Note(str(item.get("text", ""))) if isinstance(item, dict) else Note(str(item)) for item in items]
        except Exception:
            self.notes = []

    def save(self) -> None:
        data = {"notes": [note.to_dict() for note in self.notes]}
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def run(self) -> None:
        curses.wrapper(self._main)

    def _prompt(self, stdscr: curses.window, prompt: str) -> str:
        curses.echo(True)
        h, w = stdscr.getmaxyx()
        stdscr.addstr(h - 1, 0, " " * (w - 1))
        stdscr.addstr(h - 1, 0, prompt)
        stdscr.refresh()
        s = stdscr.getstr(h - 1, len(prompt), w - len(prompt) - 1)
        curses.echo(False)
        try:
            return s.decode()
        except Exception:
            return s.decode("utf-8", "ignore")

    def _compute_layout(self, width: int) -> tuple[int, int]:
        cols = 1  # Default value to ensure 'cols' is always defined
        if self.columns_config and self.columns_config > 0:
            cols = self.columns_config
        else:
            for cols in range(4, 0, -1):
                content_width = width - 1 - cols * 2 - (cols - 1)
                if content_width // cols >= 18:
                    break
        col_w = (width - 1 - (cols - 1)) // cols
        return max(1, cols), max(10, col_w)

    def _wrap_text(self, text: str, width: int) -> List[str]:
        words = text.split()
        lines, current = [], ""
        for word in words:
            if len(current) + (1 if current else 0) + len(word) > width:
                lines.append(current)
                current = word
            else:
                current = f"{current} {word}".strip()
        if current:
            lines.append(current)
        return lines if lines else [""]

    def _draw_grid(self, stdscr: curses.window, h: int, w: int) -> None:
        cols, col_w = self._compute_layout(w)
        col_heights = [0] * cols
        placements, wrapped_notes = [], []
        for note in self.notes:
            lines = self._wrap_text(note.text, col_w - 2)
            height = len(lines) + 2
            col_idx = col_heights.index(min(col_heights))
            y_off = col_heights[col_idx]
            placements.append((col_idx, y_off, height))
            wrapped_notes.append(lines)
            col_heights[col_idx] += height + 1
        content_height = h - 2
        for (col_idx, y_off, height), lines in zip(placements, wrapped_notes):
            x = col_idx * (col_w + 1)
            y = y_off - self.scroll + 1
            if y + height < 1 or y >= content_height + 1:
                continue
            if 0 <= y < content_height:
                stdscr.addstr(y, x, "+" + ("-" * (col_w - 2)) + "+")
            for i, line in enumerate(lines, start=1):
                cy = y + i
                if 0 <= cy < content_height:
                    content = line.ljust(col_w - 2)[: col_w - 2]
                    stdscr.addstr(cy, x, "|" + content + "|")
            by = y + height - 1
            if 0 <= by < content_height:
                stdscr.addstr(by, x, "+" + ("-" * (col_w - 2)) + "+")

    def _main(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.keypad(True)
        curses.use_default_colors()
        while True:
            h, w = stdscr.getmaxyx()
            stdscr.erase()
            stdscr.addstr(0, 0, "Masonry MemoPad — n: new  s: save  q: quit"[: w - 1])
            self._draw_grid(stdscr, h, w)
            stdscr.refresh()
            ch = stdscr.getch()
            if ch == ord("q"):
                break
            elif ch == ord("n"):
                text = self._prompt(stdscr, "New note: ")
                if text.strip():
                    self.notes.append(Note(text))
            elif ch == ord("s"):
                self.save()
            elif ch == curses.KEY_UP:
                self.scroll = max(0, self.scroll - 1)
            elif ch == curses.KEY_DOWN:
                self.scroll += 1

def main() -> None:
    MasonryMemoPad().run()

if __name__ == "__main__":
    main()