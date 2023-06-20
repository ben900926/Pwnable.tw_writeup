import gdb
gdb.execute('calc')
gdb.execute('b *0x804945b')
gdb.execute('b *0x8049482')
gdb.execute('run')
gdb.execute('set $eip=0x804947b')
gdb.execute('c')