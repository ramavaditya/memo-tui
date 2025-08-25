import curses
import json
import locale
import os
from dataclasses import dataclass
from typing import List
import textwrap

@dataclass
class Note:
    text: str

    def to_dict(self) -> dict:
        return {"text": self.text}

class MasonryMemoPad:
    def __init__(self, path: str = "memopad.json", columns: int | None = None) -> None:
        locale.setlocale(locale.LC_ALL, "")  # Set locale to the user's default
        self.path = path
        self.columns_config = columns
        self.notes: List[Note] = []
        self.scroll = 0
        self.load()

    def load(self) -> None:
        initial_notes = [
            Note("Press 'n' For new"),
            Note("Press 's' For save"),
            Note("Press 'q' For quit"),
            Note("Press 'e' for Last edit"),
            Note("Press 'c' For clear All"),
            Note("Hello World Its Avro"),
            Note("ようこそ世界"),
            Note("メモ取りましょう"),
        ]
        if not os.path.exists(self.path):
            self.notes = initial_notes
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("notes", []) if isinstance(data, dict) else data
            loaded_notes = [
                Note(str(item.get("text", ""))) if isinstance(item, dict) else Note(str(item))
                for item in items
            ]
            self.notes = initial_notes + loaded_notes[len(initial_notes):]  # Keep initial notes permanent
        except Exception:
            self.notes = initial_notes

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
            return s.decode(locale.getpreferredencoding())  # Decode using the preferred locale encoding
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

    def clear_notes(self) -> None:
        """Clear all notes."""
        self.notes = []

    def edit_last_note(self, stdscr: curses.window) -> None:
        """Edit the last note."""
        if not self.notes:
            return
        last_note = self.notes[-1]
        preview = " ".join(str(last_note.text).splitlines())
        h, w = stdscr.getmaxyx()
        prompt = f"Edit note: {preview[:w - 15]}"  # Truncate to fit terminal width
        new_text = self._prompt(stdscr, prompt)
        if new_text.strip():
            last_note.text = new_text

    def _main(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.keypad(True)
        curses.use_default_colors()
        while True:
            h, w = stdscr.getmaxyx()
            stdscr.erase()
            stdscr.addstr(0, 0, "Masonry MemoPad — n: new  s: save  q: quit  c: clear  e: edit last"[: w - 1])
            self._draw_grid(stdscr, h, w)
            stdscr.refresh()
            try:
                ch = stdscr.get_wch()  # Use get_wch() for wide character support
            except KeyboardInterrupt:
                break
            if ch == "q":
                break
            elif ch == "n":
                text = self._prompt(stdscr, "New note: ")
                if text.strip():
                    self.notes.append(Note(text))
            elif ch == "s":
                self.save()
            elif ch == "c":
                self.clear_notes()
            elif ch == "e":
                self.edit_last_note(stdscr)
            elif ch == curses.KEY_UP:
                self.scroll = max(0, self.scroll - 1)
            elif ch == curses.KEY_DOWN:
                self.scroll += 1

def main() -> None:
    MasonryMemoPad().run()

if __name__ == "__main__":
    main()