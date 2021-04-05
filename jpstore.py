#!/bin/env python3

import json
from sys import argv, exit, stderr
from os.path import exists
from re import split, search

class JsonSG:
    def __init__(self, file):
        self.jobject = {}
        self.file = file
        self.load(file)

    def load(self, file):
        if exists(file):
            fp = open(file)
            self.jobject = json.load(fp)
            fp.close()
        else:
            self.jobject = {}

    def save(self):
        fp = open(self.file, "w")
        fp.write(json.dumps(self.jobject, indent=4, sort_keys=True))
        fp.close()

    def jset(self,arg):
        try:
            if search("\[\.\.\]\\s*=\s*", arg):
                arg = split("\[\.\.\]\\s*=\s*", arg)
                arg = f"jobject{arg[0]}.append({arg[1]})"     
            elif search("\[\-\-\]", arg):
                arg = split("\[\-\-\]", arg)
                arg = f"del jobject{arg[0]}"
            else:
                arg = f"jobject{arg}"
            exec(arg, {"__builtins__":None},{'jobject':self.jobject})
            self.save()
            return True
        except Exception:
            print("ERROR mal-formated, not found or out of range update", file=stderr)
            return False

    def jget(self, arg):
        try:
            result = eval(f"jobject{arg}",{"__builtins__":None},{'jobject':self.jobject})
            return result
        except Exception:
            print("ERROR mal-formated, not found or out of range query", file=stderr)
            return ""

if __name__ == "__main__":
    try:
        cmd = argv[1]
        arg = argv[2]
        file = argv[3]
    except Exception:
        print("not enough arguments", file=stderr)
        exit(255)
    jsg = JsonSG(file)
    if cmd == 'set':
        exitc = jsg.jset(arg)
        if not exitc:
            exit(254)
    elif cmd == 'get':
        print(jsg.jget(arg))
    else:
        print(f"unknown command: {cmd}", file=stderr)
        exit(252)
    
    