import sys
import time
import subprocess
import logging


class SigFunctionsCon:

    def __init__(self, ourdaemon):
        self.__ourdaemon = ourdaemon

    def SIGTERM(self):
        sys.stderr.write("BB!\n")
        sys.exit(0)


class ReactFunctionCon:

    def __init__(self, ourdaemon):
        self.__ourdaemon = ourdaemon

    def start(self):
        self.__ourdaemon.start()

    def stop(self):
        self.__ourdaemon.stop()

    def restart(self):
        self.__ourdaemon.restart()

    def stmess(self, message):
        print(message)
        self.__ourdaemon.start()

    def status(self):
        self.__ourdaemon.status()

    def user(self):
        self.__ourdaemon.get_user()


class StatCon:

    strHelp = ("Autmation has be applied to distribution sistem feeder for a long time, "
               "aspecially as related to protection and the restoration of some parts of the feeder.")

    def __init__(self):
        # Настраиваем логирование
        log_file_path = 'ping_log.log'
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s %(message)s', filemode='a')
        # Указываем кодировку при открытии файла
        handler = logging.FileHandler(filename=log_file_path, encoding='utf-8')
        logging.getLogger().addHandler(handler)

    def run(self):
        #print("Метод run запущен")
        while True:
            # Выполняем пинг и получаем результат
            user_value = self.ping_host("10.101.0.135")

            # Записываем результат в лог-файл
            logging.info(user_value)
            print('LOG SUCCESSEDED', user_value)

            # Задержка перед следующим пингом
            time.sleep(10)

    def ping_host(self, host):
        """Пингует указанный хост и возвращает ответ."""
        try:
            output = subprocess.check_output(["ping", "-c", "1", host], stderr=subprocess.STDOUT)
            return output.decode()
        except subprocess.CalledProcessError as e:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            error_message = f"Ping failed at {timestamp}: {e.output.decode()}"
            return error_message

    pidFile = "/tmp/daemon-naprimer.pid"
    inputter = "/dev/null"
    outputter = "/dev/null"
    errorer = "/tmp/null"
    #errorer = "/home/espresso/lid"
