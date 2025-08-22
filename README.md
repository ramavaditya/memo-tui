# Masonry MemoPad

Masonry MemoPad is a simple, curses-based memo pad application that organizes notes in a masonry-style grid layout. It is designed to be minimalistic and user-friendly, with a focus on functionality and simplicity.

## Features

- **Masonry Grid Layout**: Notes are displayed in a grid layout, with each note dynamically adjusting its height based on its content.
- **Interactive Commands**:
  - **Add a New Note**: Press `n` to add a new note. You will be prompted to enter the note text.
  - **Save Notes**: Press `s` to save all notes to a JSON file (`memopad.json`).
  - **Quit**: Press `q` to exit the application.
  - **Scroll**: Use the arrow keys (`↑` and `↓`) to scroll through the notes if the content exceeds the terminal height.
- **Persistence**: Notes are saved to a JSON file and loaded automatically when the application starts.
- **Responsive Layout**: The number of columns adjusts based on the terminal width, ensuring an optimal viewing experience.

## Installation

1. **Install Python**: Ensure you have Python installed on your system.
2. **Install `windows-curses` (Windows Only)**: If you are using Windows, install the `windows-curses` package by running:
   ```bash
   pip install windows-curses
   ```

## Usage

1. Save the `memo.py` file to your desired directory.
2. Run the application using the following command:
   ```bash
   python memo.py
   ```
3. Interact with the memo pad using the commands described in the **Features** section.

## File Structure

- `memo.py`: The main Python script containing the application logic.
- `memopad.json`: The JSON file used for saving and loading notes. This file is created automatically when you save notes.

## How It Works

1. **Adding Notes**: When you press `n`, you are prompted to enter the text for a new note. The note is then added to the grid.
2. **Saving Notes**: Pressing `s` saves all notes to `memopad.json`. If the file already exists, it is overwritten.
3. **Grid Layout**: Notes are arranged in columns. The number of columns is determined based on the terminal width, with a maximum of 4 columns. Each note adjusts its height to fit its content.
4. **Scrolling**: If the content exceeds the terminal height, you can scroll up and down using the arrow keys.
5. **Persistence**: When the application starts, it loads notes from `memopad.json` if the file exists. If the file is missing, sample notes are displayed.

## Notes

- The application is designed to work in a terminal environment.
- It avoids dependencies beyond the Python standard library and `curses`.
- On Windows, the `windows-curses` package is required to enable `curses` functionality.

## License

This project is open-source and available under the MIT License.
