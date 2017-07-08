from itertools import islice
import os
import re


class GrepImpl:

    """
    Implementation of UNIX util grep
    """

    # number of lines to print before and after found line in log-file
    RESULT_ROW_RANGE = 100

    def __init__(self, root_dir, wildcard, numeric_id):
        """
        :param root_dir: directory to find logfile recursively
        :param wildcard: mask of log file name
        :param numeric_id: unique numeric identifier in row
        """
        self.root_dir = root_dir
        self.wildcard = re.compile(wildcard)
        self.numeric_id = numeric_id

    def process(self):
        """
        Looks for specific row in logfile and prints it within double range
        """
        log_file = self.find_log_file_by_wildcard()
        line, row_index = self.find_row_in_file(log_file)
        range_lines = self.get_row_range(log_file, row_index)
        self.print_result(log_file, line, range_lines)

    def find_log_file_by_wildcard(self):
        """
        Walks recursively in directory in search of a suitable file
        :return: absolute path of found file
        """
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                abs_path = os.path.abspath(file)
                if self.wildcard.search(abs_path):
                    return abs_path
        raise FileNotFoundError(
            "Logfile for given wildcard \"{}\" not found in \"{}\"".format(self.wildcard, self.root_dir))

    def find_row_in_file(self, file_path):
        """
        Finds row which containts unique numeric id
        :param file_path: log
        :return: tuple of wanted row and its index
        """
        goal_line, row_index = None, None

        try:
            with open(file_path, 'r') as fr:
                for row_index, line in enumerate(fr):
                    if self.numeric_id in line:
                        goal_line = line
                        break
        except:
            raise IOError("File \"{}\" is not available".format(file_path))

        if goal_line is not None:
            return goal_line, row_index
        else:
            raise ValueError("\"{}\" doesn't contain any lines with following: \"{}\"".
                             format(file_path, self.numeric_id))

    def get_row_range(self, file_path, row_index):
        """
        Gets rows before and after found index in log file
        :param file_path: log file
        :param row_index: index of found row
        :return: slice from list from minus row range or start till plus row range or end
        """
        try:
            with open(file_path, 'r') as fr:
                start = max(0, row_index - self.RESULT_ROW_RANGE)
                end = row_index + self.RESULT_ROW_RANGE + 1
                row_list = list(islice(fr, start, end))
                return row_list
        except:
            raise IOError("File \"{}\" is not available".format(file_path))

    def print_result(self, file_path, line, rows):
        """
        Prints results
        :param file_path: path to log file
        :param line: wanted string line
        :param rows: rows that will be printed
        """
        print("=== Result ===\n"
              "Log file: \"{}\"\n"
              "Wanted line: \"{}\"\n"
              "---------------\n"
              "{}".format(file_path, line.strip(), "".join(rows)))
