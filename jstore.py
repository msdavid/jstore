#!/bin/env python3

import json
from sys import argv, exit, stderr
from os.path import exists
from re import split, search
from typing import List

class JsonSG:
    def __init__(self, file=None, jstr=None):
        self.file = file
        if file:
            self.load(file)
        elif jstr:
            try:
                self.jobject = json.loads(jstr)
            except Exception:
                self.jobject = {}
                print("ERROR mal-formated, not found or out of range update", file=stderr)
        else:
            self.jobject = {}

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

    def jset(self,arg, pprint=False, raw=False):
        try:
            if search("\[\.\.\]\\s*=\s*", arg): #append new item to list
                arg = split("\[\.\.\]\\s*=\s*", arg)
                pre = f"jobject.get({arg[0][1:-1]})"
                val = eval(pre, {"__builtins__":None},{'jobject':self.jobject})
                if type(val) != list:
                   arg = f"jobject{arg[0]}=[{arg[1]}]"
                else:
                    arg = f"jobject{arg[0]}.append({arg[1]})"     

            elif search("\[\-\-\]", arg):
                arg = split("\[\-\-\]", arg)
                arg = f"del jobject{arg[0]}"

            else:
                arg = f"jobject{arg}"
            exec(arg, {"__builtins__":None},{'jobject':self.jobject})
            if self.file:
                self.save()
                return True
            if raw:
                return self.jobject
            if not pprint:
                return json.dumps(self.jobject)
            else:
                return json.dumps(self.jobject, indent=2, sort_keys=True)
        except Exception:
            print("ERROR mal-formated, not found or out of range update", file=stderr)
            return None

    def jget(self, arg, pprint=False, raw=False):
        try:
            result = eval(f"jobject{arg}",{"__builtins__":None},{'jobject':self.jobject})
            if raw:
                return result
            if not pprint:
                return json.dumps(result)
            else:
                return json.dumps(result, indent=2, sort_keys=True)
        except Exception:
            print("ERROR mal-formated, not found or out of range query", file=stderr)
            return None

if __name__ == "__main__":
    try:
        file = argv[1]
        cmd = argv[2]
        arg = argv[3]
    except Exception:
        print("not enough arguments", file=stderr)
        exit(255)
    jsg = JsonSG(file)
    if cmd == 'set':
        exitc = jsg.jset(arg)
        if not exitc:
            exit(254)
    elif cmd == 'get':
        print(jsg.jget(arg, raw=True))
    else:
        print(f"unknown command: {cmd}", file=stderr)
        exit(252)
    
    