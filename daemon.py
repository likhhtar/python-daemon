import sys
import os
import time
import signal


class SignalHandler:

    SIGNALS = ()

    def register(self, signum, callback):
        self.SIGNALS += (SigAction(signum, callback), )

    def getActions(self):
        return self.SIGNALS

    def handler(self, signum, frame):
        assert 0, "You must define a handler(signum, frame) method in %s" %(self)

    def __repr__(self):
        return "<Class:%s>" %(self.__class__.__name__)


class SigAction(SignalHandler):

    def __init__(self, signum, callback):
        self.signum = signum
        self.callback = callback
        signal.signal(self.signum, self.handler)

    def handler(self, signum, frame):
        self.callback()

    def __repr__(self):
        return "<Class:%s signal:%s>" %(self.__class__.__name__, self.signum)


class Daemon:

    def __init__(self, pidfile, stdin='/dev/null', stdout=sys.stdout, stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def metaInit(self, sigdict):
        self.sigDict = sigdict

    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(2)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(3)

        try:
            # Flush standard file descriptors

            sys.stdout.flush()
            sys.stderr.flush()

            # Open files for standard streams
            with open(self.stdin, 'r') as si, \
                    open(self.stdout, 'w') as so, \
                    open(self.stderr, 'wb', 0) as se:

                # Redirect standard file descriptors
                os.dup2(si.fileno(), sys.stdin.fileno())

                os.dup2(se.fileno(), sys.stderr.fileno())

                # Write PID to pidfile
                pid = os.getpid()
                with open(self.pidfile, 'w') as pid_file:
                    pid_file.write(f"{pid}\n")


        except OSError as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.exit(4)


    def delpid(self):
        os.remove(self.pidfile)

    def signalAssign(self):
        assignee = SignalHandler()
        for i in iter(self.sigDict):
            assignee.register(i,self.sigDict[i])

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(0)

        # Start the daemon
        self.daemonize()
        self.signalAssign()
        self.run()

    sigDict = {}

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(5)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        print('dummy')

    def status(self):
        """
        Check the status of the daemon
        """
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except FileNotFoundError:
            print("Daemon is not running.")
            return
        except ValueError:
            print("Invalid PID found in pidfile.")
            return

        print("Daemon is running with PID:", pid)

    def get_user(self):
        """
        Get a system value (e.g., current user)
        """
        system_value = os.getenv('USER')
        print(system_value)
