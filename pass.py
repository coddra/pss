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



def getmaster():
    master = getpass.getpass('Master key: ')
    while True:
        if passwordsum(dehash(masterhash, master)) == int(checksum):
            break
        master = getpass.getpass('Wrong. Master key: ')
    return master

def randompassword():
    password = bytearray()
    for i in range(24):
        password.append(random.randrange(96) + 32)
    return str(password, 'ascii')

def passwordsum(password):
    bpassword = bytes(password, 'ascii')
    sum = 0
    for i in range(len(password)):
        sum += bpassword[i]
    return sum

def searchaccounts(account):
    for i in range(len(passwords)):
        if passwords[i][0] == account:
            return i
    return None

def getaccountpassword(account):
    index = searchaccounts(account)
    if index is None:
        return None
    return passwords[index][1]

def dumpaccounts(file):
    for account in accounts:
        print(account[0], file=file)
        print(account[1], file=file)



def newpassword(prompt):
    password = getpass.getpass('New ' + prompt + ': ')
    while True:
        while len(password) < 8:
            password = getpass.getpass('Too short. New ' + prompt + ': ')
        if password == getpass.getpass('New '+ prompt + ' again: '):
            break
        password = getpass.getpass('Not matching. New ' + prompt + ': ')
    return password

def newmaster():
    return newpassword('master key')



def passsetup():
    master = newmaster()
    masterhash = randompassword()
    checksum = passwordsum(masterhash)
    file = open(path, 'w')
    print(hash(masterhash, master), file=file)
    print(checksum, file=file)
    file.close()

def getpassword(account):
    master = getmaster()
    password = getaccountpassword(account)
    if not password:
        print('No account named', account)
        return
    clipboard.copy(dehash(password, master))

def addpassword(account):
    master = getmaster()
    if prompt('Generate new password?'):
        password = randompassword()
    else:
        password = newpassword('password for ' + account)
    file = open(path, 'a')
    print(account, file=file)
    print(hash(password, master), file=file)
    file.close()



def help():
    print('Help')



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

passwords = []
while True:
    account = file.readline().rstrip()
    password = file.readline().rstrip()
    if (not account) or (not password):
        break
    passwords.append((account, password))
file.close()

if len(sys.argv) == 1 or sys.argv[1] == 'help':
    help()
elif len(sys.argv) > 2:
    if sys.argv[1] == 'get':
        getpassword(sys.argv[2])
    elif sys.argv[1] == 'add':
        if sys.argv[2] == 'master':
            print("Cannot add password for account 'master'.")
            exit()
        addpassword(sys.argv[2])
else:
    print(sys.argv[1], 'is not a command. See', sys.argv[0], 'for more information.')
