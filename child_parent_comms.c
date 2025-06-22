#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>

int main(){
	int ptc[2];
	int ctp[2];

	pipe(ptc);
	pipe(ctp);

	pid_t pid = fork();

	if(pid == 0){
		close(ptc[1]);
		close(ctp[0]);

		char buffer[BUFSIZ];
		read(ptc[0], buffer, BUFSIZ);
		printf("Child received: -%s- from parent\n", buffer);

		char *reply = "Hello from child";
		write(ctp[1], reply, strlen(reply)+1);

		exit(0);
	}else{
		close(ptc[0]);
		close(ctp[1]);

		char *msg = "Hello from parent";
		write(ptc[1], msg, strlen(msg)+1);

		char buffer[BUFSIZ];
		read(ctp[0], buffer, BUFSIZ);
		printf("Parent received:-%s- from child\n",buffer);
	}

	return 0;
}
