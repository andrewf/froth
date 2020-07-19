#!/usr/bin/env python3

import sys


def froth_binop(f):
    def frothy_op(froth):
        b = froth.pop()
        a = froth.pop()
        froth.push(f(a,b))
    return frothy_op


def branch(froth):
    # condition yes no branch
    nobranch = froth.pop()
    yesbranch = froth.pop()
    cond = froth.pop()
    toexecute = yesbranch if cond else nobranch
    # each branch is a value for now
    froth.push(toexecute)


def force_thunk(froth):
    thunk = froth.pop()
    assert(isinstance(thunk, list))
    froth.eval_block(thunk)


def print_top(froth):
    print(froth.pop())


def for_loop(froth):
    end = froth.pop()
    start = froth.pop()
    body = froth.pop()
    for i in range(start, end+1):
        froth.push(i)
        froth.eval_block(body)


def dup(froth):
    x = froth.pop()
    froth.push(x)
    froth.push(x)


class ParseState:
    def __init__(self):
        self.blockstack = []

    def parse_word(self, froth, word):
        if word == '[':
            self.blockstack.append([])
        elif word == ']':
            finished = self.blockstack.pop()
            # TODO store and return ref/label here
            if len(self.blockstack) > 0:
                self.blockstack[-1].append(finished)
            else:
                froth.eval_word(finished)
        else:
            # just a regular word
            # add to current block if there is one
            if len(self.blockstack) > 0:
                self.blockstack[-1].append(word)
            else:
                # else just emit normally
                froth.eval_word(word)


class Froth:
    def __init__(self):
        self.stack = []
        self.definitions = {
            '+': froth_binop(lambda a, b: a + b),
            '-': froth_binop(lambda a, b: a - b),
            '*': froth_binop(lambda a, b: a * b),
            '/': froth_binop(lambda a, b: a / b),
            '%': froth_binop(lambda a, b: a % b),
            '<': froth_binop(lambda a, b: a < b),
            '=': froth_binop(lambda a, b: a == b),
            'branch': branch,
            'print': print_top,
            'for': for_loop,
            'def': self.define_from_stack,
            'force': force_thunk,
            'dup': dup,
        }
        self.parser = ParseState()

    def pop(self):
        return self.stack.pop()

    def push(self, x):
        self.stack.append(x)

    def define(self, name, body):
        self.definitions[name] = body

    def define_from_stack(self, stack):
        # [ ... ] name def
        name = stack.pop()
        assert(isinstance(name, str))
        body = stack.pop()
        assert(isinstance(body, list))
        self.define(name, body)

    def eval_block(self, thunk):
        # thunk meaning block thingy
        for w in thunk:
            self.eval_word(w)

    def eval_word(self, word):
        #print('evaluating', word)
        # if it's just a block, push it like a value
        if isinstance(word, list):
            self.push(word)
            return
        body = self.definitions.get(word)
        if body is None:
            # not found in dict. treat as literal
            try:
                self.stack.append(int(word))
            except ValueError:
                self.stack.append(word)
        elif isinstance(body, list):
            # found, defined word with block body
            self.eval_block(body)
        else:
            # word with Python function body
            # create a string of stack so, in case of failure, we know what it looked like
            stack_repr = repr(self.stack)
            try:
                body(self)
            except:
                print('Stack at failure:', stack_repr)
                raise

    def toplevel_word(self, word):
        # state machine
        self.parser.parse_word(self, word)


if __name__ == '__main__':
    f = Froth()

    for line in sys.stdin:
        for word in line.split():
            f.toplevel_word(word)

