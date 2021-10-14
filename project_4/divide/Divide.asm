//R13/R14 = R15



// init vals for calc
@R15
M=0
@shiftCounter
M=1

// assign R13 val into numerator
@R13
D=M
@numerator
M=D

// assign R14 val into denominator
@R14
D=M
@denominator
M=D

// base case_1 if R13 < R14 return 0
@numerator
D=M
@denominator
D=D-M
@BASECASE_1
D;JLT


// base case_2 if R13 == R14 return 1
@numerator
D=M
@denominator
D=D-M
@INC_R15
D;JEQ

// else(R13 > R14)

(OUTERLOOP)
// check if numerator is grater then denominator
@numerator
D=M
@denominator
D=D-M
@INLOOP_1
D;JGT

// if numerator equale to denominator
@numerator
D=M
@denominator
D=D-M
@INC_R15
D;JEQ

// if numerator lesser to denominator
@END
0;JMP

(INLOOP_1)
// check if numerator > 2*denominator jump
@numerator
D=M
@denominator
D=D-M
D=D-M
@INLOOP_2
D;JLE

// else (numerator <= 2*denominator)
@denominator
M=M<<
@shiftCounter
M=M<<
@INLOOP_1
0;JMP

// add val to R15 
(INLOOP_2)
@shiftCounter
D=M
@R15
M=M+D

@shiftCounter
M=1

@denominator
D=M
@numerator
M=M-D

@R14
D=M
@denominator
M=D
@OUTERLOOP
0;JMP

(INC_R15)
@R15
M=M+1
@END
0;JMP

// handels if numerator < denominator
(BASECASE_1)
@R15
M=0
@END
0;JMP

(END)