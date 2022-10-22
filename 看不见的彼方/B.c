#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <sys/msg.h>
 
struct msg_st
{
	long int msg_type;
	char text[BUFSIZ];
};
 
int main()
{
	struct msg_st data;
	int msgtype = 0;
 	int msgid = -1;

	//建立消息队列
	msgid = msgget((key_t)1234, 0666 | IPC_CREAT);
	if(msgid == -1)
	{
		fprintf(stderr, "msgget failed with error: %d\n", errno);
		exit(EXIT_FAILURE);
	}
	
	sleep(1);
	if(msgrcv(msgid, (void*)&data, BUFSIZ, msgtype, 0) == -1)
	{
		fprintf(stderr, "msgrcv failed with errno: %d\n", errno);
		exit(EXIT_FAILURE);
	}
	printf("%s",data.text);
        
	//删除消息队列
	exit(EXIT_SUCCESS);
}