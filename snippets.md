# Language Features
These are just quick snippets to quickly go through all the main features. 
Loxscript works mostly similar to other OOP-based languages like python, java.

## Printing
```python
print "Hello World";
```
Note that LoxScript requires explicit `;` to end the statement.
## Basic Data types
```js
"this is a string";  // string
true;false;  // booleans
12;12.24;  // numbers
nil; // None
```
I would be adding lists, sets and dicts in the future.

## Arithmetic
```js
a-b;
a+b;
a/b;
c*b;
(a+b)*c; // grouping
-negate;
```
## Comparison and equality
Note: There is no implicit conversion
```js
a==b;
a!=b;
a>b;
a<b;
a>=b;
a<=b;
!true; // false
```

## Logican operators
```js
true and false; // false.
true and true;  // true.
false or false; // false.
true or false;  // true.
```
**Truthiness:** Aside from `false` and `nil` everything else is truthy 
## Variables
```js
var x = "New variable";
print x;
x = "New value"; // modifying existing variable
```
## Blockscope
Lox follows block scope
```js
{
    var x = 10;
}
print x; // error: Undefined variable x
```

## Conditionals
```js
if (a==b) {
    print "a is equal to b";
} else if (a==c) {
    print "a is equal to c";
} else {
    print "a is not equal to b";
}
```

## Looping
Lox supports `while` and `for` loop
```js
var a = 1;
while (a < 10) {
  print a;
  a = a + 1;
}
```
Equivalent `for` loop:
```js
for (var a = 1; a < 10; a = a + 1) {
  print a;
}
```

## Functions
```js
fun add(a,b) {
    return a+b;
}
print add(1, 2);
```

## Closures
Functions are first-class citizens in Lox.
```js
fun returnFunction() {
  var outside = "outside";

  fun inner() {
    print outside;
  }

  return inner;
}

var fn = returnFunction();
fn();
```

## Classes
```js
class Foo {
    init(x) {
        this.x = x;
    }
    test() {
        print ("x is " + this.x);
    }
}
var foo = Foo('VALUE OF XXXXX');
foo.test(); // x is VALUE OF XXXXX
```

## Inheritance
```js
class BaseClass {
    init() {
        this.x = 'XX';
    }
    method() {
        print "this is a method of base class!";
        print "And the value of x is " + this.x;
    }
}

class SubClass < BaseClass {
    init() {
        this.x = 'SUBCLASS';
    }
    method() {
        super.method();
    }
}
var subclass = SubClass();
subclass.method();
// This prints
// this is a method of base class!
// And the value of x is SUBCLASS
```
