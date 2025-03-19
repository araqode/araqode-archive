import os
from tools.extract.config import CHUNK_SIZE

class StreamReader:
    """
    Input content generator.
    """
    def __init__(self, chunk_size: int = CHUNK_SIZE):
        """
        Initialize the StreamReader with specified configuration.

        Args:
            chunk_size (int): Number of characters to read at a time.
        """
        self.chunk_size = chunk_size

    def read_file(self, file_path: str):
        """
        Read a file in chunks.

        Args:
            file_path (str)         : Path to the file to be read.

        Yields:
            tuple[int, list[int]]   : Chunk size, chunk of the file content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    char_codes = [ord(char) for char in chunk]
                    yield len(char_codes), char_codes
        except FileNotFoundError:
            print(f"File [{file_path}] not found!")
        except Exception as exp:
            print(f"An error occured [{str(e)}]")

    def read_folder(self, folder_path: str):
        """
        Read all files in a folder and its subdirectories and yield their content in chunks.

        Args:
            folder_path (str)           : Path to the folder containing files.

        Yields:
            tuple[str, int, list[int]]  : File name, chunk size, chunk of the file content
        """
        try:
            for root, _, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    for size, char_codes in self.read_file(file_path):
                        yield file_path, size, char_codes
        except Exception as e:
            print(f"An error occurred while reading the folder: {e}")
