/* echo_server.c: simple TCP echo server  */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <netdb.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#define MAX_CLIENTS 100

typedef struct {
	char username[100];
	int to_child_fd;
	int from_child_fd;
	pid_t pid;
} ClientEntry;


const char *HOST = NULL;
const char *PORT = "8000";
ClientEntry clients[MAX_CLIENTS] = {0};

void sigchld_handler(int signum){
	while(waitpid(-1, NULL, WNOHANG) > 0);
}

int socket_listen(const char *port){
	struct addrinfo  hints = {
        .ai_family   = AF_UNSPEC,   /* Return IPv4 and IPv6 choices */
        .ai_socktype = SOCK_STREAM, /* Use TCP */
        .ai_flags    = AI_PASSIVE,  /* Use all interfaces */
    };

	struct addrinfo *results;
    int status;

	if ((status = getaddrinfo(HOST, PORT, &hints, &results)) != 0) {
    	fprintf(stderr, "getaddrinfo failed: %s\n", gai_strerror(status));
		return -1;
    }
	
	/* For each server entry, allocate socket and try to connect */
    int server_fd = -1;
    for (struct addrinfo *p = results; p != NULL && server_fd < 0; p = p->ai_next) {
		/* Allocate socket */
		if ((server_fd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) < 0) {
	    	fprintf(stderr, "Unable to make socket: %s\n", strerror(errno));
	    	continue;
		}
	
		/* Bind socket */
		if (bind(server_fd, p->ai_addr, p->ai_addrlen) < 0) {
	    	fprintf(stderr, "Unable to bind: %s\n", strerror(errno));
	    	close(server_fd);
	    	server_fd = -1;
	    	continue;
		}

    	/* Listen to socket */
		if (listen(server_fd, SOMAXCONN) < 0) {
	    	fprintf(stderr, "Unable to listen: %s\n", strerror(errno));
	    	close(server_fd);
	    	server_fd = -1;
	    	continue;
		}
    }

	/* Release allocate address information */
    freeaddrinfo(results);

    return server_fd;

}

FILE *accept_client(int server_fd){
	struct sockaddr client_addr;
    socklen_t client_len = sizeof(struct sockaddr);

    /* Accept incoming connection */
    int client_fd = accept(server_fd, &client_addr, &client_len);
    if (client_fd < 0) {
    	fprintf(stderr, "Unable to accept: %s\n", strerror(errno));
    	return NULL;
	}

    /* Open file stream from socket file descriptor */
	FILE *client_file = fdopen(client_fd, "w+");
	if (!client_file) {
    	fprintf(stderr, "Unable to fdopen: %s\n", strerror(errno));
    	close(client_fd);
	}

	return client_file;
}

int main(int argc, char *argv[]) {

	if(argc == 2) PORT = argv[1];
    
  	int server_fd = socket_listen(PORT);
	if(server_fd < 0){
		return EXIT_FAILURE;
	}
    
	printf("Server connected on PORT: %s\n",PORT);

	// Place signal handler
	signal(SIGCHLD, sigchld_handler);

    /* Process incoming connections */
    while (1) {

		FILE* client_file = accept_client(server_fd);
		if(!client_file) continue;
		pid_t pid = fork();

		if(pid == 0){ // child
			/*TODO handle request function */

        	/* Read from client, parse message and send to parent */
        	char buffer[BUFSIZ];
        	while (fgets(buffer, BUFSIZ, client_file)) {
            	fputs(buffer, stdout);
            	fputs(buffer, client_file);
        	}

        	/* Close connection */
        	fclose(client_file);
			exit(EXIT_SUCCESS);

		}else if(pid > 0){ // parent
			fclose(client_file);	
		}else if(pid < 0){ // error
			fprintf(stderr, "Unable to fork: %s\n", strerror(errno));
		}
    }

    return EXIT_SUCCESS;
}

/* vim: set expandtab sts=4 sw=4 ts=8 ft=c: */
