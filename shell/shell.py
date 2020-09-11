import os, sys, time, re

while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ('$$ ').encode())
            try:
                userInput = input()
            except EOFError:
                sys.exit(1)

        if userInput == "": # Empty input, will prompt again
            continue
        if 'exit' in userInput: # Terminates shell
            break
        if 'cd' in userInput: # Change directory
                if '..' in userInput:
                        changeDir = '..'
                else:
                        changeDir = userInput.split('cd')[1].strip()
                try:
                        os.chdir(changeDir)
                except FileNotFoundError:
                        pass
                continue
        pid = os.getpid()
        os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

        rc = os.fork()

        if rc < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

        elif rc == 0:                   # child
                os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" %(os.getpid(), pid)).encode())
                args = userInput.split()
                if '>' in userInput: # Redirect output
                        userIn = userInput.split('>')
                        os.close(1)                 # redirect child's stdout
                        sys.stdout = open(userIn[1], "w")
                        os.set_inheritable(1, True)
                        parent = userIn[0].split()
                        path(parent)
                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                        program = "%s/%s" % (dir, args[0])
                        check = 0
                        os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                        try:
                                os.execve(program, args, os.environ) # try to exec program
                                check = 1
                        except FileNotFoundError:             # ...expected
                                #os.write(1, ("%s Command not found\n"%args[0]).encode())
                                pass                              # ...fail quietly

                if check == 0:
                        os.write(1,("%s Command not found\n"%args[0]).encode())
                os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error

        else:                           # parent (forked ok)
                os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" %(pid, rc)).encode())
                childPidCode = os.wait()
                os.write(1, ("Parent: Child %d terminated with exit code %d\n"%childPidCode).encode())
