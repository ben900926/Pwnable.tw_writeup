# 3x17 (150 pts)

checksec 
```
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    No canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

The program is asking for address and data
```
addr:
data:
```

By the way, this program is stripped, so I was having a hard time understanding functions :(

## Examine function
start entry is located at 0x401a50 (readelf -h 3x17)
```
00401a50 31  ed           XOR        EBP ,EBP
00401a52 49  89  d1       MOV        R9,RDX
00401a55 5e              POP        RSI
00401a56 48  89  e2       MOV        RDX ,RSP
00401a59 48  83  e4  f0    AND        RSP ,-0x10
00401a5d 50              PUSH       RAX
00401a5e 54              PUSH       RSP =>local_10
00401a5f 49  c7  c0       MOV        R8=>FUN_00402960 ,FUN_00402960
            60  29  40  00
00401a66 48  c7  c1       MOV        RCX =>FUN_004028d0 ,FUN_004028d0
            d0  28  40  00
00401a6d 48  c7  c7       MOV        RDI =>first_func ,first_func
            6d  1b  40  00
00401a74 67  e8  36       CALL       FUN_00401eb0                                     undefined FUN_00401eb0(undefined
            04  00  00

```
This is actually the code for __libc_start_main(main, argc, argv & env, init, fini, ...) </br>
The main() is loacted in $rdi (located in 0x401b6d)

~~By triggering signal, I found that the input syscall triggered in 0x446e2c (Why would someone do that?)~~

stored buffer located in $esp - 28, this buffer stores address input
seems this input is processed by FUN_0040ee70(buffer). </br>
> Remember return value is stored in $rax ?

We can examine its functionality dynamically.
So, when I entered 2048, the program give me "0x800"; when enter 1024, output "0x400".</br>
FUN_0040ee70 is basically strtol().

This functionality makes it possible to rewrite addresses with input values. But... unlike the previous challenge (chal), there's no output of stack address information.

## Where I got stucked :(
Note that except main function, there're two special functions being called in _lib_start_main</br>
In function 0x4028d0, .init(0x401000) and .init_array(0x4b40e0) are called.
Also, function 0x402960 call .fini and .fini_array, I know its address and it's writable!

Here is the execution flow:

```
func. 0x4028d0 (.init) --> _libc_start_main --> main --> func 0x402960 (.fini_array[1] --> .fini_array[0] --> .fini)
```
In "ret_cycle", I fill .fini_array[1] with address of main and [0] with address of func 0x402960. </br>
That way, when func 0x402960 is called after main() done executing, main() and func 0x402960 are executed again.

*I want to do ROP... but how do I write value to stack ? I do not know its address*
## Frame Faking

Let's examine _libc_csu_fini function more closer
``` 
    00402960 55               PUSH       RBP
    00402968 48  8d  2d       LEA        RBP ,[PTR_FUN_004b40f0 ]                          = 00401b00
                81  17  0b  00
```
At the start, 0x4b40f0 is pushed to $rbp

In the end,
```
    00402996 48  83  c4  08    ADD        RSP ,0x8
    0040299b 5d                POP        RBP
```
mov rbp, rsp ; rbp = [rsp] = 0x4b40f0, rsp = 0x4b40f0
pop rbp      ; rbp = [rsp] = [0x4b40f0], rsp = 0x4b40f8
ret          ; rip = [rsp] = [0x4b40f8], rsp = 0x4b4100

0x4b40f0 : rbp (.fini_array[0]) | 0x4b40f8 : rip (.fini_array[1]) | 0x4b4100 : rsp | ROP shellcode...

Now, we know that where $rsp is located at the end of fini_function
We can try to write an address at $rsp, then call the "leave ret" gadget located at the end of main()
In this way, $rip will be covered with value located on $rsp

## ROP gadgets
0x000000000041e4af : pop rax ; ret --> 59
0x0000000000401696 : pop rdi ; ret --> char* filename
0x0000000000406c30 : pop rsi ; ret --> 0
0x0000000000446e35 : pop rdx ; ret --> 0
0x00000000004022b4 : syscall

## Bingo!
FLAG{Its_just_a_b4by_c4ll_0riented_Pr0gramm1ng_in_3xit}