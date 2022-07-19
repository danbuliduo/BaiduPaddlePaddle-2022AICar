
with open('/proc/meminfo') as fd:
    for line in fd:
        if line.startswith('MemTotal'):
            total = line.split()[1]
            continue
        if line.startswith('MemFree'):
            free = line.split()[1]
            break
TotalMem = int(total)/1024.0
FreeMem = int(free)/1024.0
print( "FreeMem:"+"%.2f" % FreeMem+'M')
print( "TotalMem:"+"%.2f" % TotalMem+'M')