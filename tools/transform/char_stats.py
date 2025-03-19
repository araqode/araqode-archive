from tools.extract.stream_reader import StreamReader

class FileStats:
    def __init__(self):
        self.total_chars: int = 0
        self.unique_char_set: dict[str, int] = {}

class FolderStats(FileStats):
    def __init__(self):
        super().__init__()
        self.file_stats: dict[str, FileStats] = {}

class CharStatistics:
    """
    Generate statistics for StreamReader.
    """
    def __init__(self, stream_reader: StreamReader):
        """
        Initialize CharStatistics with specified configuration.

        Args:
            stream_reader (StreamReader): Input content generator.
        """
        self.stream_reader = stream_reader

    def collect(self, folder_path: str):
        """
        Collect statistics for all files under folder.

        Args:
            folder_path (str)   : Path to the content folder.

        Returns:
            FolderStats         : Folder statistics and file statistics.
        """
        folder_stats = FolderStats()

        for file_path, chunk_size, chunk in self.stream_reader.read_folder(folder_path):
            if file_path not in folder_stats.file_stats:
                folder_stats.file_stats[file_path] = FileStats()
            file_stats = folder_stats.file_stats[file_path]
            
            file_stats.total_chars += chunk_size
            folder_stats.total_chars += chunk_size

            for char in chunk:
                if char not in file_stats.unique_char_set:
                    file_stats.unique_char_set[char] = 1
                else:
                    file_stats.unique_char_set[char] += 1

                if char not in folder_stats.unique_char_set:
                    folder_stats.unique_char_set[char] = 1
                else:
                    folder_stats.unique_char_set[char] += 1

        return folder_stats