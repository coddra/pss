#!/usr/bin/env python

import getpass
import os
import sys
import getpass
import random
import clipboard

def touch(path):
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    with open(path, 'a'):
        os.utime(path, None)

def getch():
    return sys.stdin.read(1)

def prompt(question):
    print(question, '(Y/n) ', end='', flush = True)
    c = getch().lower()
    return c == 'y' or c == '\n'

def bhash(bpassword, bmaster):
    return (bpassword + bmaster - 64) % 96 + 32

def hash(password, master):
    bpassword = bytes(password, 'ascii')
    bmaster = bytes(master, 'ascii')
    hashed = bytearray()
    for i in range(len(password)):
        hashed.append(bhash(bpassword[i], bmaster[i % len(master)]))
    return str(hashed, 'ascii')

def bdehash(bpassword, bmaster):
    return (bpassword + 96 - bmaster) % 96 + 32

def dehash(password, master):
    bpassword = bytes(password, 'ascii')
    bmaster = bytes(master, 'ascii')
    dehashed = bytearray()
    for i in range(len(password)):
        dehashed.append(bdehash(bpassword[i], bmaster[i % len(master)]))
    return str(dehashed, 'ascii')



def requestmaster():
    master = getpass.getpass('Master key: ')
    while True:
        if accountsum(dehash(masterhash, master)) == int(checksum):
            break
        master = getpass.getpass('Incorrect. Master key: ')
    return master

def randompassword():
    password = bytearray()
    for i in range(24):
        password.append(random.randrange(96) + 32)
    return str(password, 'ascii')

def accountsum(password):
    bpassword = bytes(password, 'ascii')
    sum = 0
    for i in range(len(password)):
        sum += bpassword[i]
    return sum

def searchaccounts(account):
    for i in range(len(accounts)):
        if accounts[i][0] == account:
            return i
    return None

def accountpassword(account):
    index = searchaccounts(account)
    if index is None:
        return None
    return accounts[index][1]

def dumpdata():
    file = open(path, 'w')
    print(masterhash, file=file)
    print(checksum, file=file)
    for account in accounts:
        print(account[0], file=file)
        print(account[1], file=file)
    file.close()



def requestnewpassword(prompt):
    password = getpass.getpass('New ' + prompt + ': ')
    while True:
        while len(password) < 8:
            password = getpass.getpass('Too short. New ' + prompt + ': ')
        if password == getpass.getpass('Confirm '+ prompt + ': '):
            break
        password = getpass.getpass('Incorrect. New ' + prompt + ': ')
    return password

def requestnewmaster():
    return requestnewpassword('master key')



def passsetup():
    master = requestnewmaster()
    masterhash = randompassword()
    checksum = accountsum(masterhash)
    file = open(path, 'w')
    print(hash(masterhash, master), file=file)
    print(checksum, file=file)
    file.close()

def getpassword(account):
    master = requestmaster()
    password = accountpassword(account)
    if not password:
        print('No account named', account)
        return
    clipboard.copy(dehash(password, master))

def addpassword(account):
    if account == 'master':
        print("Cannot add password for account 'master'.")
        exit()
    master = requestmaster()
    if prompt('Generate new password automatically?'):
        password = randompassword()
    else:
        password = requestnewpassword('password for ' + account)
    file = open(path, 'a')
    print(account, file=file)
    print(hash(password, master), file=file)
    file.close()

def setmaster():
    global masterhash, checksum
    master = requestmaster()
    newmaster = requestnewmaster()
    masterhash = randompassword()
    checksum = accountsum(masterhash)
    masterhash = hash(masterhash, newmaster)
    for i in range(len(accounts)):
        accounts[i] = (accounts[i][0], hash(dehash(accounts[i][1], master), newmaster))
    dumpdata()

def setpassword(account):
    global accounts
    master = requestmaster()
    password = requestnewpassword('password for ' + account)
    index = searchaccounts(account)
    if not index:
        print('No account named', account)
        return
    accounts[index] = (accounts[index][0], hash(password, master))
    dumpdata()

def setcommand(account):
    if account == 'master':
        setmaster()
    else:
        setpassword(account)

def deleteaccount(account):
    requestmaster()
    index = searchaccounts(account)
    if not index:
        print('No account named', account)
        return
    del(accounts[index])
    dumpdata()



def usage(command):
    return command + ' [' + commands[command][0] + ']'

def seehelp():
    return "See '" + sys.argv[0] + " help' for more information."

def helpof(command):
    result = '   ' + command
    if commands[command][0]:
        result += ' <' + commands[command][0] + '>'
    else:
        result += '         '
    return result + '      ' + commands[command][2]

def helpcommand():
    print('Usage:', sys.argv[0], '<command> [arg]')
    print()
    print('Avaible commands:')
    for command in commands:
        print(helpof(command))



commands = {
    'add': ('account', addpassword, 'Add a new account and adherent password'),
    'del': ('account', deleteaccount, 'Remove account and adherent password'),
    'get': ('account', getpassword, 'Copy the password to clipboard'),
    'set': ('account', setcommand, 'Change the password of an account'),
    'help': (None, helpcommand, 'Display this help message')
}

if len(sys.argv) == 1 or sys.argv[1] == 'help':
    helpcommand()
    exit()


if not sys.argv[1] in commands:
    print("'" + sys.argv[1] + "'", 'is not a command.', seehelp())
    exit()

if len(sys.argv) == 2:
    print('Usage:', sys.argv[0], usage(sys.argv[1]))
    print(seehelp())
    exit()



path = '/home/' + getpass.getuser() + '/.config/pass.words'



if not os.path.isfile(path):
    touch(path)

file = open(path)
masterhash = file.readline().rstrip()
checksum = file.readline().rstrip()

if (not masterhash) or (not checksum):
    file.close()
    if prompt('Pass is not set up. Set up now?'):
        passsetup()
    exit()

accounts = []
while True:
    account = file.readline().rstrip()
    password = file.readline().rstrip()
    if (not account) or (not password):
        break
    accounts.append((account, password))
file.close()



commands[sys.argv[1]][1](sys.argv[2])
