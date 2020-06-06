Abbey
=============

Abbey is a Python-like  language interpreter written in [python](https://www.python.org)

it is developed as hobby interpreter and for learning purpose



Abbey is based on complete rewrite of [Abrvalg](https://github.com/akrylysov/abrvalg) with code improvement and  more strict parsing and addition of new features,

Features in abbey different from [Abrvalg](https://github.com/akrylysov/abrvalg)

* Class
* keywords to function declaration and function call
* new keywords
* string formating
* Exception handling
* method call
* conditional assignment
* multiple assignment
* importing python modules
* importing  module
* .foreach iteration
* break condition
* continue condition


### Class
```py

class BankAccount(name,balance):
    this.name = name
    this.balance = balance

    func deposit(amount):
        this.balance = this.balance + amount

    func withdraw(amount):
        if amount > this.balance:
            return  'insufficient balance'
        this.balance = this.balance - amount
        return this.balance
    func changename(name):
        this.name = name
        return name
    func tranfer(amount,account):
        s = this.withdraw(amount)
        balance = this.balance
        m = "transfer #{amount} to #{account} new balance is #{balance}"
        return m


bank = BankAccount('bank user',100)
write(bank.name) # bank user
write(bank.balance) #100
bank.withdraw(45)
write(bank.balance) # 55
bank.deposit(123)
write(bank.balance) # 178
response = bank.tranfer(40,123634367)
write(response) # tranfer 40 to 123634367 new balance 138
resp = bank.withdraw(56343)
write(resp) # 'insufficient balance'
new_name = bank.changename('new username')
write(new_name == bank.name) # True
bank.name = 'changed name'
write(bank.name) # changed name

class Calc: # class with  no parameters
    this.name = 'calc'
```

### Function keywords
```py
func greet(name,times=10):
    for i in 1...times:
        write(name)
func add(num,num):# raise error, multiple args 'num'
    return num + num
func add(num,other=3,other=8) # raise error, multiple kwargs for 'other'
greet('abbey') #print 10 times
greet('abbey',times=3) #print 3 times
greet('abbey',t=5) # raise error, unknown keyword 't'
```

### new keywords
```py
and
a and b

or
a  or b

in
'h' in 'hello' # True

'pick' in ['pick','pack'] # True

not 

not 's' in 'hello' # True
not 'h' in 'hello' # False
use # for importing module from python
use os
use os as __os
use re as regex
include function in "file.ab" # importing abbey function
```


### String formatting
```py
name = "Abbey"
version = 1
repo = 'github'
write("this is #{name} lang, version #{version} on #{repo}") # this is Abbey lang version 1 on github
```
### Exception
```js
try:
    k = unknown
catch:
    write('hooops an error ocuurs')
```

```py
try:
    k = unknow
catch err:
    write(err.name)  ## NameError
    write(err.message)  ## name 'unknown' is not define
```
### conditional assignment

```py
url = 'https'
msg = 'secure' ? url == 'https' : 'not secure'
n = 'yes' ? 'a' in 'abcd' and 1 == 2 : 'no'
write(n) # no
write(msg) ## 'secure'
```
## multiple assignment
```py
name, email, password = 'myname','myemail','mypassword'
write(name)
write(email)
write(password)
f,g,k = 1,2,3,8  # raise error, left items(3) not equals right(4)
a = 1,2,3,4,5,6,6,7 # will be converted to list  
write(a)  #[1,2,3,4,5,6,6,7]
write(a[2]) # 3
```

## method call
```py
name = 'helloword'
out = name.upper.lower.isalpha
write(out)  # True

# parsing arguments
k = '__helloo'
h = k.lstrip('_').count('l')
write(h)
```
#### .foreach

```py
seq.foreach => item:
    write(item)
 ## seq can be string, array, dict or number

num = 123456780
num.foreach => i:
    if i > 4:
        write(i)  # 5, 6, 7, 8
array = ['a','b','c','end','d']
array.foreach => str:
    if str == 'end':
        break
    write(str)
```
### importing  python module
```py
use os  # import os
write(os.getcwd)

use re as regex
m = regex.compile('[a-z]')
f = m.search('hello')
write(f)
```
7. hhjh

## importing local module
```py
# in bank.ab

class BankAccount(name,balance):
    this.name = name
    this.balance = balance

    func deposit(amount):
        this.balance = this.balance + amount

    func withdraw(amount):
        if amount > this.balance:
            return  'insufficient balance'
        this.balance = this.balance - amount
        return this.balance
    func changename(name):
        this.name = name
        return name
    func tranfer(amount,account):
        s = this.withdraw(amount)
        response = 'tranfer '+ amount + ' to '+ account +' new balance ' + this.balance
        return response


# in main.ab
include BankAccount in "bank.ab"


bank = BankAccount("username",100)
write(bank.balance) #100
bank.withdraw(45)
write(bank.balance) # 55
bank.deposit(123)
write(bank.balance) # 178
response = bank.tranfer(40,123634367)
write(response) # tranfer 40 to 123634367 new balance 138
resp = bank.withdraw(56343)
write(resp) # 'insufficient balance'
new_name = bank.changename('new username')
write(new_name == bank.name) # True




```
### Break and Continue condition
```py
# prints out 4,5,6,7
p = [1,2,3,4,5,9,4,3,7,8,9,10]
p.foreach => num:
    break ? num == 8 # break if num == 8
    continue ? num in [1,2,3] # continue if num in [1,2,3]
    write(num)
```
## Setup
**Prerequsite**:<br/>
    - Install [python](https://www.python.org)<br/>




## running test
inside main folder
run `python -m unittest`


### Running interpreter
To execute  program, run 
inside main folder `python main.py <file>`.
there are files in [examples](/examples) folder
run `python main.py examples/<filename>`



### Issuses

 Abbey use indentation(whitespace) to indicate block of code like python ,so there may be exception raising or source not being parse properly if there is inconsistency in use of tab and spaces. 

 ### credits
   * [Abrvalg](https://github.com/akrylysov/abrvalg)
