#! /usr/bin/env python3

import os, sys, time, re

def path(args):
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                #os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                                #Previous error given by sending whole userInput to look for it
                                #which created addition of values from input text and output text
                                #to be stored in the output text, by specifying only wc and input
                                # file it fixed the problem
                        os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

        #os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

def redirect(direction, userInput):
        userInput = userInput.split(direction)
        if direction == '>':
                os.close(1)
                sys.stdout = open(userInput[1].strip(), "w")
                os.set_inheritable(1, True)
                path(userInput[0].split())
        else:
                os.close(0)
                sys.stdin = open(userInput[1].strip(), 'r')
                os.set_inheritable(0, True)
                path(userInput[0].split())
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
        #os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
        rc = os.fork()
        if rc < 0:
                #os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)
        elif rc == 0:                   # child

                #os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" %(os.getpid(), pid)).encode())
                args = userInput.split()
                

                if "|" in userInput: # Piping command
                        pipe = userInput.split("|")
                        pipeCommand1= pipe[0].split()
                        pipeCommand2 = pipe[1].split()

                        pr, pw = os.pipe()  # file descriptors pr, pw for reading and writing
                        for f in (pr, pw):
                                os.set_inheritable(f, True)
                        pipeFork = os.fork()
                        if pipeFork < 0:  # fork failed
                                #os.write(2, ('Fork failed').encode())
                                sys.exit(1)

                        if pipeFork == 0: # child - will write to pipe
                                os.close(1) # redirect child's stdout
                                os.dup(pw)
                                os.set_inheritable(1, True)
                        
                                for fd in (pr, pw):
                                        os.close(fd)
                                path(pipeCommand1)    
                        else: # parent (forked ok)
                                os.close(0)
                                os.dup(pr)
                                os.set_inheritable(0, True)
                                for fd in (pw, pr):
                                        os.close(fd)
                                path(pipeCommand2)
        
                                
                if '>' in userInput:
                        redirect('>', userInput)
                elif '<' in userInput:
                        redirect('<', userInput)
                else:
                        if '/' in args[0]:
                                program = args[0]
                                try:
                                        os.execve(program,args,os.environ)
                                except FileNotFoundError:
                                        pass
                        else:
                                path(args)


        else:                           # parent (forked ok)
                if not '&' in userInput:
                        #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" %(pid, rc)).encode())
                        childPidCode = os.wait()
                        #os.write(1, ("Parent: Child %d terminated with exit code %d\n" %childPidCode).encode())
                
