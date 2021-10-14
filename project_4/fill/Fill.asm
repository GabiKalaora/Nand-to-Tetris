// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.




(INITIAL)
    @SCREEN
    D=A
    @screenAddres
    M=D


(LOOP)
    @KBD
    D=M

    @ON
    D;JNE
    @OFF
    D;JEQ

(ON)
    @x
    D = M
    @screenAddres
    A = M
    M = D

    M = -1

    @screenAddres
    D = M + 1
    M = D

    @KBD
    A=A-1
    D=D-A
    @ON
    D;JLT


(OFF)
    @x
    D = M
    @screenAddres
    A = M
    M = D

    M = 0

    @screenAddres
    D = M + 1
    M = D

    @KBD
    A=A-1
    D=D-A
    @OFF
    D;JLT

    @INITIAL
    0;JMP



