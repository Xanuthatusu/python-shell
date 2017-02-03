#!/usr/local/bin python

import os
import sys
import string
import subprocess
import signal

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

jobs = {}

currentForegrounds = []

def handleSignal(signum, stackFrame):
  global currentForeground
  global parent

  pid, sig = os.waitpid(-1, os.WNOHANG)
  if pid in currentForegrounds:
    currentForegrounds.remove(pid)
    if sig == 512:
      commandFailed = True
    return

  else:
    del jobs[pid]
    if sig == 0:
      sys.stdout.write(Color.OKGREEN + "\nProgram with PID: " + str(pid) + " exited successfully!\n" + Color.ENDC + os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
    else:
      sys.stdout.write(Color.FAIL + "\nProgram with PID: " + str(pid) + " exited with a non-zero!\n" + Color.ENDC + os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
    sys.stdout.flush()

def handleCtrlC(signum, stackFrame):
  print(Color.FAIL + "\nExiting!" + Color.ENDC)
  sys.exit()

signal.signal(signal.SIGCHLD, handleSignal)
signal.signal(signal.SIGINT, handleCtrlC)

def handlePiping(cmd):
  r, w = os.pipe()
  pid = os.fork()
  index = cmd.index("|")

  if pid == 0:
    first = cmd[:index].split()

    os.close(r)
    os.dup2(w, 1)
    os.close(w)

    os.execvp(first[0], first)

  else:
    currentForegrounds.append(pid)

  pid = os.fork()

  if pid == 0:
    second = cmd[index+1:].split()

    os.close(w)
    os.dup2(r, 0)
    os.close(r)

    os.execvp(second[0], second)

  else:
    os.close(w)
    os.close(r)
    currentForegrounds.append(pid)

def handleCd(cmd):
  global commandFailed

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

def handleRedirection(cmd):
  while len(cmd) > 2 and cmd[-2] in (">", "<", ">>"):
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

  handleNormal(cmd)

def handleNormal(cmd):
  try:
    os.execvp(cmd[0], cmd)
  except:
    print(Color.FAIL + "Invalid command" + Color.ENDC)
    commandFailed = True
    sys.exit()

while True:
  if len(currentForegrounds):
    continue

  if commandFailed:
    sys.stdout.write(Color.FAIL + "X " + Color.ENDC + os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
  else:
    sys.stdout.write(os.getcwd().replace(os.getenv("HOME"), "~") + " > ")
  sys.stdout.flush()

  commandFailed = False

  cmd = sys.stdin.readline()

  if "|" in cmd:
    handlePiping(cmd)

  else:
    if cmd == "":
      sys.exit(1)

    cmd = cmd.split()

    if len(cmd) == 0:
      continue

    if cmd[0] == "exit" or cmd[0] == "quit":
      sys.exit(1)

    elif cmd[0] == "cd":
      handleCd(cmd)

    elif cmd[0] == "jobs":
      for job in jobs:
        print(str(job) + " " + str(jobs[job]))

    else:
      pid = os.fork()

      if pid == 0:
        if cmd[-1] == "&":
          cmd = cmd[:-1]

        if len(cmd) > 2 and cmd[-2] in (">", "<", ">>"):
          handleRedirection(cmd)

        handleNormal(cmd)

      else:
        if cmd[-1] != "&":
          currentForegrounds.append(pid)
        else:
          jobs[pid] = cmd[0]
