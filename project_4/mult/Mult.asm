// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    //PSEUDO CODE:
    //  x = R1
    //  y = R0
    //  sum = 0
    //  R2 = 0
    // LOOP:
    //      if x == 0 goto STOP
    //      else if x < 0 then sum = sum - y and x = x + 1
    //      else sum = sum + y and x = x - 1
    // STOP:
    //      R2 = sum


    // INITIAL VARIBALS AND R2
    @R1
    D=M
    @x
    M=D // x = R1

    @R0
    D=M
    @y
    M=D // y = R0

    @0
    D=A
    @R2
    M=D // R2 = 0

    @sum
    M=0 // sum = 0

(LOOP)

    // if R1 less or equal to 0 goyo STOP
    @x
    D=M
    @STOP
    D;JEQ 
 
    // if R1 < 0 goto NEGATIV
    @x
    D=M
    @NEGATIV
    D;JLT

    // else sum = sum + R0
    @y
    D=M
    @sum
    M=D+M
    // and R1 = R1 - 1
    @1
    D=A
    @x
    M=M-D
    @LOOP
    0;JMP

(NEGATIV)
    // sum = sum - R0
    @y
    D=M
    @sum
    M=M-D

    // and R1 = R1 + 1
    @1
    D=A
    @x
    M=M+D
    @LOOP
    0;JMP


(STOP)
    @sum
    D=M
    @R2
    M=D

(END)
    @END
    //0;JMP
