__copyright__ = """
    This file is part of the TouchPortal-API project.
    Copyright (c) TouchPortal-API Developers/Contributors
    All rights reserved.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime, date, time
from json import JSONEncoder, dumps
from logging import Formatter, getLogger, getLevelName, StreamHandler, NullHandler, Handler
from logging.handlers import TimedRotatingFileHandler

class Logger:
    """ A helper class for common logging requirements, which can be configured via the constructor and provides some convenience
    methods.

    It uses an instance of Python's `logging.Logger()` class, either the one specified in the `logger` constructor parameter,
    or, if `logger` is `None`, one obtained with `logging.getLogger(name=name)`.
    Any logger interactions which are not directly supported by this helper class can be accessed directly via `Logger.logger` member.

    Due to the how Python's logger works, the first ("root") instance of the logger will define the defaults for any named loggers
    added later. These defaults can optionally be overridden per child instance by passing the desired parameters to the constructor
    or via the `setLogLevel()`, `setStreamDestination()`, and `setFileDestination()` methods.

    The class provides aliases for the `logging.Logger` log writing methodss like `debug()`, `info()`, 'log()', etc.
    In addition, some shorter aliases are provided (`dbg()`, `inf()`, `wrn()/warn()`, `err()`, `crt()/fatal()`).

    For further details on Python's built-in logging, see: https://docs.python.org/3/library/logging.html
    """

    """ The default options to use for `TimedRotatingFileHandler`. """
    DEFAULT_FILE_HANDLER_OPTS:dict = {'when': 'D', 'backupCount': 7, 'delay': True}
    """ The default log formatter for stream and file logger handlers. """
    DEFAULT_LOG_FORMATTER = Formatter(
        fmt="{asctime:s}.{msecs:03.0f} [{levelname:.1s}] [{filename:s}:{lineno:d}] {message:s}",
        datefmt="%H:%M:%S", style="{"
    )

    def __init__(self, name=None, level=None, stream=None, filename=None, logger=None,
                formatter=DEFAULT_LOG_FORMATTER,
                fileHandlerOpts=DEFAULT_FILE_HANDLER_OPTS ):
        """
        Creates an instance of the logger.

        Args:
            `name`: A name for this logger instance. Each named logger is a global instance, specifying an existing name will use that instance.
                The "root" logger has no name.
            `level`: Logging level for this logger. `None` will keep the default (root or existing) logger level.
            `stream`: Add an instance of `logging.StreamHandler()` with specified stream (eg. `os.stderr`).
            `filename`: Add an instance of `logging.handlers.TimedRotatingFileHandler()` with specified file name.
                By default the logs are rotated daily and the last 7 files are preserved. This can be changed via the `fileHandlerOpts` argument.
            `logger`: Use specified `logging.Logger()` instance. By default a logger instance is created/retreived using `logging.getLogger(name=name)`.
            `formatter`: Use specified `logging.Formatter()` as the formatter for the added stream and/or file handlers.
                By default the static `DEFAULT_LOG_FORMATTER` is used.
            `fileHandlerOpts`: Additional parameters for `TimedRotatingFileHandler` logger.
        """
        # Create/get logger instance unless specified
        self.logger = logger if logger else getLogger(name=name)
        # use default formatter unless specified
        self.formatter = formatter if formatter else self.DEFAULT_LOG_FORMATTER
        # store instance of file/stream handler for possible future access to them (eg. to set logging level)
        self.fileHandler = None
        self.streamHandler = None
        self.nullHandler = None
        # logging function aliases
        self.log                              = self.logger.log
        self.dbg = self.debug                 = self.logger.debug
        self.inf = self.info                  = self.logger.info
        self.wrn = self.warn  = self.warning  = self.logger.warning
        self.err = self.error                 = self.logger.error
        self.crt = self.fatal = self.critical = self.logger.critical
        self.exception                        = self.logger.exception
        # set logging level if specified
        if level:
            self.setLogLevel(level)
        # add file log if a filename was specified
        if filename:
            self.setFileDestination(filename, fileHandlerOpts)
        # add a stream handler if requested or as fallback for failed file logger above
        if stream:
            self.setStreamDestination(stream)

    def setLogLevel(self, level, logger=None):
        """
        Set the miniimum logging level, either globally for all log handlers (`logger=None`, the default), or a specific instance.
        `level` can be one of:  "CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG" (or equivalent Py `logging` module Level constants),
        or `None` to disable all logging.
        """
        if logger:
            if isinstance(level, Handler):
                logger.setLevel(level)
            return

        currentLevel = None if self.nullHandler else self.logger.getEffectiveLevel()
        if level and isinstance(level, str):
            level = getLevelName(level)  # actually gets the numeric value from a name
        if level == currentLevel:
            return
        if level:
            self.logger.setLevel(level)
            # if switching from null logging, remove null handler and re-add stream/file handler(s)
            if self.nullHandler:
                self.logger.removeHandler(self.nullHandler)
                self.nullHandler = None
                if self.fileHandler:
                    self.logger.addHandler(self.fileHandler)
                if self.streamHandler:
                    self.logger.addHandler(self.streamHandler)
        else:
            # switch to null logging, remove known file handlers if they exist and set null handler with critical level
            if self.fileHandler:
                self.logger.removeHandler(self.fileHandler)
            if self.streamHandler:
                self.logger.removeHandler(self.streamHandler)
            self.nullHandler = NullHandler()
            self.logger.addHandler(self.nullHandler)
            self.logger.setLevel("CRITICAL")

    def setStreamDestination(self, stream):
        """ Set a destination for the StreamHandler logger. `stream` should be a file stream type (eg. os.stderr) or `None` to disable. """
        if self.streamHandler:
            self.logger.removeHandler(self.streamHandler)
            self.streamHandler = None
        if stream:
            try:
                self.streamHandler = StreamHandler(stream)
                self.streamHandler.setFormatter(self.formatter)
                self.logger.addHandler(self.streamHandler)
            except Exception as e:
                print(f"Error while creating stream logger: \n{repr(e)}")

    def setFileDestination(self, filename, handlerOpts = DEFAULT_FILE_HANDLER_OPTS):
        """ Set a destination for the File logger. `filename` should be a file name (with or w/out a path) or `None` to disable the file logger. """
        if self.fileHandler:
            self.logger.removeHandler(self.fileHandler)
            self.fileHandler = None
        if filename:
            try:
                if not os.path.splitext(filename)[1]:
                    filename += ".log"
                self.fileHandler = TimedRotatingFileHandler(str(filename), **handlerOpts)
                self.fileHandler.setFormatter(self.formatter)
                self.logger.addHandler(self.fileHandler)
            except Exception as e:
                print(f"Error while creating file logger: \n{repr(e)}")

    class JsonEncoder(JSONEncoder):
        """ Custom JSON encoder for handling `dataclass` types and pretty-printing date/time types. Used for `format_json()` method. """
        def default(self, obj):
            if is_dataclass(obj):
                return asdict(obj)
            if isinstance(obj, (datetime, date, time)):
                return obj.isoformat()
            return super(Logger.JsonEncoder, self).default(obj)

    @staticmethod
    def format_json(data, indent=2):
        """ Returns a string representation of an object, serialized to JSON and formatted for human-readable output (such as logging). """
        return dumps(data, cls=Logger.JsonEncoder, indent=indent)
