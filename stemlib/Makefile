all: stmr

stmr: stmr.c
	 gcc -shared -Wl,-soname,stmr -o stmr.so -fPIC stmr.c

clean:
	rm *o