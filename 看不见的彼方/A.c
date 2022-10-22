#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/msg.h>
#include <errno.h>
 #include<fcntl.h>

#define MAX_TEXT 512
struct msg_st
{
	long int msg_type;
	char text[MAX_TEXT];
};
 
int main()
{
	struct msg_st data;
	char buffer[BUFSIZ];
	int msgid = -1;
 
	//建立消息队列
	msgid = msgget((key_t)1234, 0666 | IPC_CREAT);
	if(msgid == -1)
	{
		fprintf(stderr, "msgget failed with error: %d\n", errno);
		exit(EXIT_FAILURE);
	}
 
    int fd = open("secret", O_RDONLY);
    while(read(fd, buffer, sizeof(buffer))>0)
    {
    }
		
    data.msg_type = 1;
    strcpy(data.text, buffer);
    //向队列发送数据
    if(msgsnd(msgid, (void*)&data, MAX_TEXT, 0) == -1)
    {
        fprintf(stderr, "msgsnd failed\n");
        exit(EXIT_FAILURE);
    }

	exit(EXIT_SUCCESS);
}