#!/usr/local/bin python

import os
import sys
import string
import subprocess

class Color():
    HEADER = "\x1b[95m"
    OKBLUE = "\x1b[94m"
    OKGREEN = "\x1b[92m"
    WARNING = "\x1b[93m"
    FAIL = "\x1b[91m"
    ENDC = "\x1b[0m"
    BOLD = "\x1b[1m"
    UNDERLINE = "\x1b[4m"

Color = Color()

commandFailed = False

while True:
  if commandFailed:
    sys.stdout.write(Color.FAIL + "X " + Color.ENDC + os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
  else:
    sys.stdout.write(os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
  sys.stdout.flush()

  commandFailed = False

  split = os.fork()

  if split == 0:
    cmd = sys.stdin.readline()
    if cmd == "":
      sys.exit(1)

    cmd = cmd.split()

    if len(cmd) == 0:
      continue

    if cmd[0] == "exit" or cmd[0] == "quit":
      sys.exit(1)
    elif cmd[0] == "cd":
      if len(cmd) == 1:
        os.chdir(os.getenv("HOME"))
      else:
        if cmd[1] == "~":
          cmd[1] = os.getenv("HOME")
        try:
          os.chdir(cmd[1])
        except:
          print(Color.FAIL + "File not found" + Color.ENDC)
          commandFailed = True

    else:
      pid = os.fork()

      if pid == 0:
        while len(cmd) > 2 and (cmd[-2] in (">", "<", ">>")):
          outFile = os.path.abspath(cmd[-1])

          operation = cmd[-2]
          cmd = cmd[:-2]

          if operation == ">":
            fd = os.open(outFile, os.O_WRONLY|os.O_TRUNC|os.O_CREAT, 0o644)

            os.dup2(fd, 1)

          elif operation == ">>":
            fd = os.open(outFile, os.O_WRONLY|os.O_APPEND)

            os.dup2(fd, 1)

          elif operation == "<":
            try:
              fd = os.open(outFile, os.O_RDONLY)

              os.dup2(fd, 0)

            except:
              print(Color.FAIL + "File not found" + Color.ENDC)
              commandFailed = True

        try:
          os.execvp(cmd[0], cmd)
        except:
          print(Color.FAIL + "Invalid command" + Color.ENDC)
          sys.exit(2)
      else:
        if os.waitpid(pid, 0)[1] == 512:
          commandFailed = True

  else:
    os.waitpid(split, 0)
    sys.exit()
