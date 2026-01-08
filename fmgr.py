import os
import shutil


class ConsoleIO:
    def write(self, msg: str) -> None:
        print(msg)

    def read(self, prompt: str) -> str:
        return input(prompt)


class FileExplorer:
    def __init__(self, start_path=None, fs=os, io=None):
        self.fs = fs
        self.io = io or ConsoleIO()
        self.current_path = start_path or self.fs.path.expanduser("~")

    def list_dir(self):
        return self.fs.listdir(self.current_path)

    def display_directory_contents(self):
        try:
            contents = self.list_dir()
            self.io.write(f"\nCurrent Directory: {self.current_path}")
            self.io.write("-" * 50)
            for index, element in enumerate(contents):
                full_path = self.fs.path.join(self.current_path, element)
                kind = "📁 Folder" if self.fs.path.isdir(full_path) else "📄 File"
                self.io.write(f"{index}. {kind}: {element}")
            return contents
        except Exception as e:
            self.io.write(f"Error: {e}")
            return []

    def navigate(self, index):
        try:
            contents = self.list_dir()
            element = contents[index]
            full_path = self.fs.path.join(self.current_path, element)
            if self.fs.path.isdir(full_path):
                self.current_path = full_path
                return True
            self.io.write(f"Cannot open file {element}")
            return False
        except Exception as e:
            self.io.write(f"Navigation error: {e}")
            return False

    def go_to_parent_directory(self):
        self.current_path = self.fs.path.dirname(self.current_path)


class FileSelector:
    def __init__(self, fs=os, io=None):
        self.fs = fs
        self.io = io or ConsoleIO()
        self.selected_files = []
        self.current_directory_contents = []

    def load_directory_contents(self, directory_path):
        try:
            self.current_directory_contents = self.fs.listdir(directory_path)
            return self.current_directory_contents
        except Exception as e:
            self.io.write(f"Error loading directory contents: {e}")
            return []

    def select_files_by_indices(self, indices, directory_path):
        try:
            self.selected_files.clear()
            chosen = [int(i.strip()) for i in indices.split(",") if i.strip() != ""]
            for index in chosen:
                if 0 <= index < len(self.current_directory_contents):
                    full_path = self.fs.path.join(directory_path, self.current_directory_contents[index])
                    self.selected_files.append(full_path)
            self.io.write("Selected files:")
            for file in self.selected_files:
                self.io.write(f" - {self.fs.path.basename(file)}")
            return list(self.selected_files)
        except Exception as e:
            self.io.write(f"Selection error: {e}")
            return []

    def get_selected_files(self):
        return list(self.selected_files)

    def clear_selection(self):
        self.selected_files.clear()


class FileManager:
    def __init__(self, explorer, selector, fs=os, ops=shutil, io=None):
        self.explorer = explorer
        self.selector = selector
        self.fs = fs
        self.ops = ops
        self.io = io or ConsoleIO()

    def copy_files(self, destination):
        try:
            for file in self.selector.get_selected_files():
                if self.fs.path.exists(file):
                    self.ops.copy2(file, destination)
            self.io.write(f"{len(self.selector.get_selected_files())} file(s) copied")
            self.selector.clear_selection()
        except Exception as e:
            self.io.write(f"Copy error: {e}")

    def move_files(self, destination):
        try:
            for file in self.selector.get_selected_files():
                if self.fs.path.exists(file):
                    self.ops.move(file, destination)
            self.io.write(f"{len(self.selector.get_selected_files())} file(s) moved")
            self.selector.clear_selection()
        except Exception as e:
            self.io.write(f"Move error: {e}")

    def delete_files(self):
        try:
            for file in self.selector.get_selected_files():
                if self.fs.path.isfile(file):
                    self.fs.remove(file)
                elif self.fs.path.isdir(file):
                    self.ops.rmtree(file)
            self.io.write(f"{len(self.selector.get_selected_files())} file(s)/folder(s) deleted")
            self.selector.clear_selection()
        except Exception as e:
            self.io.write(f"Delete error: {e}")


def main_menu():
    io = ConsoleIO()
    explorer = FileExplorer(fs=os, io=io)
    selector = FileSelector(fs=os, io=io)
    manager = FileManager(explorer, selector, fs=os, ops=shutil, io=io)

    while True:
        io.write("\n--- File Explorer ---")
        io.write("1. Display Directory")
        io.write("2. Navigate")
        io.write("3. Go to Parent Directory")
        io.write("4. Select Files")
        io.write("5. Copy")
        io.write("6. Move")
        io.write("7. Delete")
        io.write("8. Quit")

        choice = io.read("Your choice: ")

        if choice == "1":
            contents = explorer.display_directory_contents()
            selector.current_directory_contents = contents

        elif choice == "2":
            index = int(io.read("Enter navigation index: "))
            explorer.navigate(index)
            contents = explorer.display_directory_contents()
            selector.current_directory_contents = contents

        elif choice == "3":
            explorer.go_to_parent_directory()
            contents = explorer.display_directory_contents()
            selector.current_directory_contents = contents

        elif choice == "4":
            contents = explorer.display_directory_contents()
            selector.current_directory_contents = contents
            indices = io.read("Enter file indices to select (comma-separated): ")
            selector.select_files_by_indices(indices, explorer.current_path)

        elif choice == "5":
            dest = io.read("Enter destination path for copying: ")
            manager.copy_files(dest)

        elif choice == "6":
            dest = io.read("Enter destination path for moving: ")
            manager.move_files(dest)

        elif choice == "7":
            manager.delete_files()

        elif choice == "8":
            io.write("Goodbye!")
            break

        else:
            io.write("Invalid choice")


if __name__ == "__main__":
    main_menu()
