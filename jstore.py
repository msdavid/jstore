#!/bin/env python3

import json
from sys import argv, exit, stderr
from os.path import exists
from re import split, search
from typing import List
import argparse
from os import environ
from shlex import shlex

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
    
    def split_semicolon(self, strg):
        lex = shlex(strg)
        lex.whitespace=""
        tokens = list(lex)
        if ";" in tokens:
            result = []
            comp = ""
            for token in tokens:
                if token == ";":
                    result.append(comp)
                    comp=""
                    continue
                comp += token
            result.append(comp)
            return result
        return [strg]


    def jset(self, args, pprint=False, raw=False):
        # try:
            for arg in self.split_semicolon(args):
                print(arg)
                if search("\[\.\.\]\\s*=\s*", arg): #append new item to list
                    arg = split("\[\.\.\]\\s*=\s*", arg.strip())
                    pre = f"jobject.get({arg[0][1:-1]})"
                    val = eval(pre, {"__builtins__":None},{'jobject':self.jobject})
                    if type(val) != list:
                        arg = f"jobject{arg[0]}=[{arg[1]}]"
                    else:
                        arg = f"jobject{arg[0]}.append({arg[1]})"     

                elif search("\[\-\-\]", arg): #delete item
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
        # except Exception:
        #     print("ERROR mal-formated, not found or out of range update", file=stderr)
        #     return None

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
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="set or get", choices=['set', 'get'])
    parser.add_argument("querystring", help="query string")
    parser.add_argument("-j", "--json", help="returns json formated resuts ", action="store_true")
    parser.add_argument("-f", "--filename", help="file name. If not specified it will be $HOME/.jstore")
    args = args = parser.parse_args()
    if not args.filename:
        args.filename = environ['HOME'] + "/.jstore"
    jsg = JsonSG(args.filename)
    if args.cmd == 'set':
        exitc = jsg.jset(args.querystring)
        if not exitc:
            exit(254)
    elif args.cmd == 'get':
        print(jsg.jget(args.querystring, raw=(not args.json)))
    