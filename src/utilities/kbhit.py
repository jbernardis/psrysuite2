import msvcrt


class KBHit:
    def __init__(self):
        pass

    def getch(self):
        c = msvcrt.getch()
        try:
            return c.decode('utf-8')
        except UnicodeDecodeError:
            print("\nnon utf8: %d" % ord(c))
            c = msvcrt.getch()
            print("next char: %d" % ord(c))
            return None

    def kbhit(self):
        return msvcrt.kbhit()


# Test    
if __name__ == "__main__":

    kb = KBHit()
    cmd = ""

    print('Hit any key, or ESC to exit')

    while True:
        if kb.kbhit():
            c = kb.getch()
            if c is None:
                continue
                
            if ord(c) == 27: # ESC
                break
            
            if ord(c) == 13 : # enter ley
                print("\ncommand: %s" % cmd)
                print(cmd[:-1])
                for c in cmd:
                    print(ord(c))
                cmd = ""
            elif ord(c) == 8: # backspace
                if len(cmd) > 0:
                    cmd = cmd[:-1]
                print("\r%s \r%s" % (cmd, cmd), end="", flush=True)
            else:
                print(c, end="", flush=True)
                cmd += c
