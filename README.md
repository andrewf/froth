# Froth

A very slapdash forth-like language interpreter, written in an afternoon to make me feel better.

Anything that's not a recognized word is pushed to the stack as a literal.
Blocks, delimited by `[]`, are also pushed to the stack.
There is a `force` word that executes a block (aka thunk) at the top of the stack.
There are enough arithmetic primitives to write a fahrenheit-to-celsius converter and FizzBuzz.
New words are defined by pushing a block for the body, a name, and running the `def` word.
