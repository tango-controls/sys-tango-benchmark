
import os
import tango
import subprocess


class ServerProcessManager(object):

    def __init__(self, name, starter=None):
        self.__name = name
        self.__starter = starter
        self.__proc = None
        self.__stdout = None

    def __enter__(self):
        if self.__starter is not None:
            self.__starter.DevStart(self.__name)
        else:
            self.__stdout = open(os.devnull, 'w')
            self.__proc = subprocess.Popen(
                self.__name.split('/'),
                stdout=self.__stdout,
                stderr=self.__stdout,
                shell=False)

        return tango.DeviceProxy("dserver/" + self.__name.lower())

    def __exit__(self, *args):
        if self.__starter is not None:
            try:
                self.__starter.DevStop(self.__name)
            except tango.DevFailed:
                self.__starter.HardKillServer(self.__name)
        else:
            self.__proc.terminate()
            self.__proc.wait()
            self.__stdout.close()
