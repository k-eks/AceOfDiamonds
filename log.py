import time

class Logger():
    """Handles the file IO for the Kagome lattice"""

    def __init__(self, fileName, filePath):
        """Constructor
        fileName ... string name of the file created by the logger"""
        now = time.localtime()
        self.fileName = "%s_%s%s%s_%s%s.asc" % (fileName, now[0], now[1], now[2], now[3], now[4])
        self.filePath = filePath
        # file creation
        self.log = open(self.filePath + self.fileName, 'w+', 1)


    def __del__(self):
        """Destructor, cleaning up"""
        self.log.close()


    def log_text(self, message):
        """Writes a textline with time stamp to the logger.
        message ... string text to be written"""
        self.log.write(time.strftime("%c") + ": %s\n" % message)


    def log_simple_text(self, message):
        """Writes a textline to the logger.
        message ... string text to be written"""
        self.log.write("%s\n" % message)


    def log_xy(self, x, y):
        """Writes data in the xy-format to the logger.
        x ... number value of x axis
        y ... number value of y axis"""
        self.log.write("%s;%s\n" % (x, y))