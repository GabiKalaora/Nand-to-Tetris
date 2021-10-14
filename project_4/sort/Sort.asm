@i
M=1
@j
M=1




(OUTLOOP)
@j
M=1

// get size of arr
@R15
D=M
@lenArr
M=D

// get address begining of array
@R14
D=M
@aAdress
M=D

@i
D=M
@lenArr
D=M-D
@END
D;JEQ


(INLOOP)

@j  
D=M
@aAdress  
A=M  
D=M
@aValue 
M=D

@aAdress
D=M+1
@bAdress
M=D
A=D
D=M
@bValue 
M=D


//check if need to swap
@bValue
D=M
@aValue
D=D-M

@SWAP
D;JGT

//else
@j
M=M+1
D=M
@lenArr
D=M-D
@aAdress
M=M+1 
@INLOOP
D;JGT

@i
M=M+1
@OUTLOOP
0;JMP


(SWAP)
@aValue
D=M
@bAdress
A=M
M=D


@bValue
D=M
@aAdress
A=M
M=D


@j
M=M+1
D=M
@lenArr
D=M-D
@aAdress
M=M+1 
@INLOOP
D;JGT

@OUTLOOP
0;JMP


(END)