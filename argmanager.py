import argparse


class ArgManager:

    """
    Class to define arguments and get their values
    """

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Search in file by IP-address,log wildcard and numeric ID')
        self.parser.add_argument('-ip', '--ipaddress', help='IP-address', required=True)
        self.parser.add_argument('-w', '--wildcard', help='Wildcard of log name', required=True)
        self.parser.add_argument('-id', help='Numeric identifier', required=True)

    @property
    def passed_args(self):
        """
        Fetches argument values
        :return: ip, mask and numeric ID
        """
        args = self.parser.parse_args()
        return args.ipaddress, args.wildcard, args.id
