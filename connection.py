from ftplib import FTP


#: abstract database dictionary with credentials by ip-address
DB = {
    "127.0.0.1": ("login", "password")
}


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
