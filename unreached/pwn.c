#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/reg.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/user.h>
#include <signal.h>
#include <fcntl.h>

int main()
{
    pid_t child;
    long orig_eax;
    child = fork();
    if (child == 0)
    {
        ptrace(PTRACE_TRACEME, 0, NULL, NULL);

        // int devNull = open("/dev/null", 0);
        // dup2(devNull, STDIN_FILENO);
        // dup2(devNull, STDOUT_FILENO);
        // close(devNull);

        execl("./chall", "./chall", NULL);
    }
    else
    {
        int status;
        struct user_regs_struct regs;
        unsigned long base;

        wait(&status);
        if (WIFEXITED(status) || WIFSIGNALED(status))
        {
            exit(EXIT_FAILURE);
        }

        while (1)
        {
            ptrace(PTRACE_SINGLESTEP, child, 0, 0);
            wait(&status);
            if (WIFEXITED(status) || WIFSIGNALED(status))
            {
                exit(EXIT_FAILURE);
            }

            struct user_regs_struct regs;
            ptrace(PTRACE_GETREGS, child, 0, &regs);

            if ((regs.rcx >> 44) == 5)
            {
                // printf("get base addr: 0x%lx\n", regs.rcx);
                base = regs.rcx - 0x40;
                break;
            }

            // printf("{{ 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx 0x%lx }}\n", regs.rip, regs.rax, regs.rbx, regs.rcx, regs.rdx, regs.rdi, regs.rsi, regs.rbp, regs.rsp, regs.r8, regs.r9, regs.r10, regs.r11, regs.r12, regs.r13, regs.r14, regs.r15);
        }

        while (1)
        {
            ptrace(PTRACE_SYSCALL, child, 0, 0);
            wait(&status);
            if (WIFEXITED(status))
            {
                break;
            }

            if (WIFSIGNALED(status))
            {
                exit(EXIT_FAILURE);
            }

            struct user_regs_struct regs;
            ptrace(PTRACE_GETREGS, child, 0, &regs);
            if (regs.orig_rax == 0x1)
            {
                // printf("get syscall write\n");
                // write
                regs.rdx = 0x4000;
                regs.rsi = base;
                ptrace(PTRACE_SETREGS, child, NULL, &regs);
            } else {
                continue;
            }

            // get write syscall result
            ptrace(PTRACE_SYSCALL, child, 0, 0);
            wait(&status);
            if (WIFEXITED(status) || WIFSIGNALED(status))
            {
                exit(EXIT_FAILURE);
            }

            ptrace(PTRACE_GETREGS, child, 0, &regs);
            // printf("syscall write with result: 0x%llx\n", regs.rax);

            ptrace(PTRACE_CONT, child, 0, 0);
            ptrace(PTRACE_DETACH, child, 0, 0);
        }

        // while (1)
        // {
        //     // enter next syscall
        //     ptrace(PTRACE_SYSCALL, child, 0, 0);
        //     wait(&status);
        //     if (WIFEXITED(status))
        //     {
        //         break;
        //     }

        //     struct user_regs_struct regs;
        //     ptrace(PTRACE_GETREGS, child, 0, &regs);

        //     unsigned long long int orig_rax = regs.orig_rax;
        //     unsigned long long int rip = regs.rip;
        //     unsigned long long int rbp = regs.rbp;
        //     unsigned long long int rax = regs.rax;
        //     unsigned long long int rdx = regs.rdx; // count
        //     unsigned long long int rsi = regs.rsi; // buffer
        //     unsigned long long int rdi = regs.rdi; // fd
        //     unsigned long long int rsp = regs.rsp;
        //     // write syscall 可以把修改buffer到base addr 让进程加载到内存的elf 打到stdout 对付111权限很有用
        //     if (orig_rax == 1)
        //     {
        //         printf("syscall write triggered, rip: 0x%llx, rbp: 0x%llx, rax: 0x%llx, rdx(count): 0x%llx, rsi(buffer): 0x%llx, rdi(fd): 0x%llx, rsp: 0x%llx\n",
        //         rip, rbp, rax, rdx, rsi, rdi, rsp);
        //     }
        //     else {
        //         continue;
        //     }

        //     int fd = open("/tmp/dump", O_CREAT|O_APPEND|O_WRONLY, 0644);
        //     // dump memory 4096bytes
        //     for(int i=0; i<0x1000; i+=4) {
        //         long data = ptrace(PTRACE_PEEKTEXT, child, rsi+i, 0);
        //         write(fd, &data, 4);
        //     }
        //     close(fd);

        //     // get write syscall result
        //     // [todo] return check
        //     ptrace(PTRACE_SYSCALL, child, 0, 0);
        //     wait(&status);
        //     if (WIFEXITED(status))
        //     {
        //         break;
        //     }
        //     // [todo] return check
        //     ptrace(PTRACE_GETREGS, child, 0, &regs);
        //     printf("syscall write with result: 0x%llx\n", regs.rax);

        //     ptrace(PTRACE_KILL, child, 0, 0);
        //     ptrace(PTRACE_DETACH, child, 0, 0);
        //     wait(&status);
        //     if (WIFSIGNALED(status))
        //     {
        //         break;
        //     }
        // }
    }
    return 0;
}