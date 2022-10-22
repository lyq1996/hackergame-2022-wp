## 0x05 看不见的彼方

这里分析源码，发现socket系统调用虽然被ban了，但是我们还有消息队列呀，两个进程只要使用同一个key即可访问同一个消息队列。

A.c将secret放到消息队列里：
```
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
```

B.c从消息队列里取secret：
```
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
        
	// [todo] 删除消息队列
	exit(EXIT_SUCCESS);
}
```
编译上传，即可获得flag。
