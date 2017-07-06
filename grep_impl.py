# -*- coding: utf-8 -*-
"""This module represents python grep implementation with server connection"""

import argparse
from ftplib import FTP
import os
import re

#: abstract database dictionary with credentials by ip-address
DB = {
    "127.0.0.1": ("login", "password")
}


class ArgManager:

    """
    Class to define arguments and get their values
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Search in file by IP-address,log wildcard and numeric ID')
        self.parser.add_argument('-a', '--ipaddress', help='IP-address', required=True)
        self.parser.add_argument('-w', '--wildcard', help='Wildcard of log name', required=True)
        self.parser.add_argument('-i', '--id', help='Numeric identifier', required=True)

    @property
    def passed_args(self):
        """
        Fetches argument values
        :return: ip, mask and numeric ID
        """
        args = self.parser.parse_args()
        return args.ipaddress, args.wildcard, args.id


class ServerConnection:

    """
    Class to retrieve credentials from database and setup connection to server
    """

    def __init__(self, host):
        self._conn = None
        self.host = host
        self.user, self.password = self.get_auth_data()
        self.connect()
        self.login()

    def get_auth_data(self):
        """
        Gets credentials from DB by ip address
        :return: tuple of login and password
        """
        return DB[self.host]

    def connect(self):
        """
        Connects to server and shows welcome message sent by server
        """
        self._conn = FTP(self.host)
        print(self._conn.getwelcome())

    def login(self):
        """
        Logs in server with given credentials
        """
        self._conn.login(self.user, self.password)

    def disconnect(self):
        """
        Closes connection on server
        """
        self._conn.quit()

    @property
    def cd(self):
        """
        :return: current directory on server
        """
        return self._conn.pwd()


class GrepImpl:

    """
    Implementation of UNIX util grep
    """

    #: number of lines to print before and after found line in log-file
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
        log_file = self.find_log_file_by_wildcard(self.root_dir)
        file_lines = self.read_lines_from_file(log_file)
        row_index = self.find_row_in_file(file_lines)
        rows = self.get_rows_in_range(file_lines, row_index)
        self.print_result(log_file, rows)

    def find_log_file_by_wildcard(self, directory, wildcard):
        """
        Walks recursively in directory in search of a suitable file
        :param directory: root directory to start search
        :param wildcard: mask of logfile name
        :return: absolute path of found file
        """
        for root, _, files in os.walk(directory):
            for file in files:
                abs_path = os.path.abspath(file)
                if wildcard.search(abs_path):
                    return abs_path
        raise FileNotFoundError(
            "Logfile for given wildcard \"{}\" not found in \"{}\"".format(directory, wildcard))

    def read_lines_from_file(self, file_path):
        """
        Reads all lines from file once
        :param file_path: file path to read lines from
        :return: list of lines
        """
        try:
            with open(file_path, 'r') as fr:
                return fr.readlines()
        except:
            raise IOError("File \"{}\" is not available".format(file_path))

    def find_row_in_file(self, file_lines):
        """
        Finds row which containts unique numeric id
        :param file_lines: list of lines from log file
        :return: index of found row
        """
        for row_index, line in enumerate(file_lines):
            if self.numeric_id in line:
                return row_index
        raise ValueError("Not found row with following: {}".format(self.numeric_id))

    def get_rows_in_range(self, file_lines, row_index):
        """
        Gets rows before and after found index in log file
        :param file_lines: list of lines from log file
        :param row_index: index of found row
        :return: slice from list from minus row range or start till plus row range or end
        """
        start_index = max(0, row_index - self.RESULT_ROW_RANGE)
        end_index = min(len(file_lines), row_index + self.RESULT_ROW_RANGE + 1)
        return file_lines[start_index:end_index]

    def print_result(self, file_path, rows):
        """
        Prints results
        :param file_path: path to log file
        :param rows: rows that will be printed
        """
        print("=== Result ===\n"
              "Log file: {}\n"
              "---------------\n"
              "{}".format(file_path, rows))


def main():
    """
    Main function to fetch args, connect to server, find info in file and disconnects from server
    """
    try:
        ip_address, wildcard, num_id = ArgManager().passed_args
        connection = ServerConnection(host=ip_address)

        GrepImpl(root_dir=connection.cd,
                 wildcard=wildcard,
                 numeric_id=num_id).process()

        connection.disconnect()

    except Exception as err:
        print("=== Error ===\n{}\n{}".format(err.__class__, str(err)))


if __name__ == '__main__':
    main()
