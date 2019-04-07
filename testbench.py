#!/usr/bin/env python3

import os
import sys

#Globals
FILENAME = "system_tb"
TIME = "#10;\n"
INTERACTIVE = False  #indicates whether arguments will be entered as flags or after being prompted
COMPTEST = True     #indicates whether the tests in the testbench will cover all possible 
                    #combinations of binary values, or only those specified when running the script
INPUTLIST = []      #will contain the inputs to the testbench
OUTPUTLIST = []     #outputs from the test bench
SYSTEMINPUTS = []   #will contain the inputs to the system module or the unit otherwise under test
SYSTEMOUTPUTS = []  #will contain the outputs from the same unit
TESTLIST = []       #if comprehensive test is not used, will contain the values to be used in each
                    #test

#Functions
def usage(status=0):
    #display usage information and exit with specified status
    print('''Usage: {} -i [inputs] -o [outputs] -si [system inputs] -so [system outputs] [options]

    -h                                               Display usage
    -interactive                                     Will run the program in interactive input mode
    -i  [largestbitnumber:smallestbitnumber]input    Testbench inputs (example: [3:0]testA)
                                                                      (default: if size is not 
                                                                       specified, it will be set
                                                                       to one bit)
    -o  [largestbitnumber:smallestbitnumber]output   Testbench outputs (example: [6:0]H0)
    -si System Input Names                           System inputs
    -so System Output Names                          System outputs
    -f  FILENAME                                     Desired testbench file name
    -t  TIME                                         Length of each individual test
    -bv Binary Test Values                           The binary values to be used for each testcase
                                                    (note: number of values must be a multiple of
                                                     the number of inputs, or each input will not
                                                     have a value for every test)
    -dv Decimal Test Values                          The decimal values to be used for each testcase
    -hv Hexadecimal Test Values                      The hex values to be used for each testcase

    '''.format(os.path.basename(sys.argv[0])))
    sys.exit(status)

def io(fileName, inputs, outputs):
    #generate the I/O of the testbench
    for input in inputs:
        fileName.write("\treg " + input + ";\n")
    for output in outputs:
        fileName.write("\twire " + output + ";\n")

    fileName.write("\n")

def uut(fileName, inputList, outputList, systemInputs, systemOutputs, testList, time):
    #generate the unit under test portion of the testbench
    listLoc = 0
    numBitsList = []

    for item in inputList:  #finds the size of each input in bits, then strips the characters 
                            #indicating this, changing the list to contain just the input name
        letterLoc = 0
        if item[0] != '[':  #executes if the size is 1 bit
            numBitsList.append('1')
            continue
        else:
            for letter in item:
                if letter != ']':
                    letterLoc += 1
                else:       #locates the character indicating the size in bits
                    numBits = item[:letterLoc]
                    numBits = int(item[1]) + 1
                    numBitsList.append(numBits)
                    letterLoc += 1
                    item = item[letterLoc:]
                    inputList[listLoc] = item #replaces the input name and size with just the name
                    listLoc += 1

    listLoc = 0
    for item in outputList: #strips the characters indicating the size of the output and changes
                            #the output list to contain only the names of the outputs
        letterLoc = 0
        if item[0] != '[':
            continue
        else:
            for letter in item:
                if letter != ']':
                    letterLoc += 1
                else:
                    letterLoc += 1
                    item = item[letterLoc:]
                    outputList[listLoc] = item
                    listLoc += 1

    fileName.write("\t")
    for letter in FILENAME: #determines the name of the unit under test from the name of the
                            #testbench file
        if letter != '_':
            fileName.write(letter)
        else:
            break
    fileName.write(" uut(\n")

    #prints each of the corresponding system and tesbench inputs and outputs for the uut portion of
    #the testbench
    for number in range(len(systemInputs)):
        fileName.write("\t\t." + systemInputs[number] + " (" + inputList[number] + "),\n")
    for number in range(len(systemOutputs)):
        if max(range(len(systemOutputs))) - number > 0:
            fileName.write("\t\t." + systemOutputs[number] + " (" + outputList[number] + "),\n")
        else: #makes sure that the last line of the unit under test doesn't end in a comma
            fileName.write("\t\t." + systemOutputs[number] + " (" + outputList[number] + ")\n")
    fileName.write("\t);\n\n")

    if COMPTEST == True:
        comprehensiveTest(fileName, inputList, numBitsList, time)
    else:
        Test(fileName, inputList, testList, numBitsList, time)

def Test(fileName, inputList, testList, numBitsList, time):
    #generate the sets of values to test from the values specified by the -v command
    fileName.write("\tinitial begin\n")

    for test in testList:
        inputLoc = 0
        fileName.write("\t\t")
        for value in test:
            while len(value) < numBitsList[inputLoc]:
                value = "0" + value
            fileName.write(inputList[inputLoc] + " = " + str(numBitsList[inputLoc])+ "'b")
            fileName.write(value + "; ")
            inputLoc += 1
        fileName.write("\n\t\t" + time)

    fileName.write("\n\t$stop;\n\tend\nendmodule\n")

def comprehensiveTest(fileName, inputs, numBitsList, time):
    #generates every possible test given the sizes of the inputs
    fileName.write("\tinitial begin\n\t\t")
    inputDict = {}
    inputLoc = 0

    for item in inputs: #creates a nested dictionary containing information about each input
        inputSubDict = {}
        inputSubDict["length"] = numBitsList[inputLoc]
        inputSubDict["max"] = (2**numBitsList[inputLoc]) - 1
        inputSubDict["value"] = 0
        inputDict[item] = inputSubDict
        inputLoc += 1
  
    printCases(fileName, inputDict, inputs, time)
    fileName.write("\n\t$stop;\n\tend\nendmodule\n")

def printCases(fileName, inputDict, inputs, time):
    #think of the following code as a series of counters. The rightmost counter counts upwards from
    #zero. When it reaches its maximum value, the counter to its left increments. This goes on until
    #the leftmost counter has reached its maximum value, meaning that each possible combination
    #of values has been covered.
    while inputDict[inputs[0]]["value"] <= inputDict[inputs[0]]["max"]: #while every possible combo
                                                                        #has not been covered
        incLoc = -1
        finishedFlag = False
        while inputDict[inputs[incLoc]]["value"] == inputDict[inputs[incLoc]]["max"]:
        #executes when a counter reaches its maximum. Will go through each counter until it finds
        #one that has not reached its maximum.
            if inputs[incLoc] == inputs[0]: #if the counter at its maximum being checked is the
                                            #leftmost one, the test generation is finished
                finishedFlag = True
                break
            inputDict[inputs[incLoc]]["value"] = 0 #set the current counter to zero
            incLoc -= 1                            #and check the next one
        if finishedFlag == True:
            break

        inputDict[inputs[incLoc]]["value"] += 1 #increment the counter found to not be at its max
        inputLoc = 0
        generateBinary(fileName, inputs, inputDict, inputLoc)
        
        fileName.write("\n\t\t" + time + "\t\t")

def generateBinary(FileName, inputs, inputDict, inputLoc):
    for item in inputs:
            #generate the binary value to be assigned to the input (e.g. 3'b010)
            inputDict[inputs[inputLoc]]["binVal"] = str(inputDict[inputs[inputLoc]]["length"])
            inputDict[inputs[inputLoc]]["binVal"] += "'b"
            binaryValue = bin(inputDict[inputs[inputLoc]]["value"])[2:]
            #finds the binary equivalent of the value expressed in as few digits as possible

            while len(binaryValue) < int(inputDict[inputs[inputLoc]]["length"]):
            #appends zeros to the front of the binary value until its size is equivalent to the
            #number of bits of its corresponding input
                binaryValue = "0" + binaryValue
            inputDict[inputs[inputLoc]]["binVal"] += binaryValue
            fileName.write(item + " = " + inputDict[inputs[inputLoc]]["binVal"] + "; ")
            inputLoc += 1

#Command line options
args = sys.argv[1:]

if not len(args):
    usage()

while len(args) and args[0].startswith('-'):
    arg = args.pop(0)
    if (arg == "-h"):
        usage()
    elif (arg == "-interactive"):
        INTERACTIVE = True
        break
    elif (arg == "-f"):       #set filename
        arg = args.pop(0)
        FILENAME = arg + "_tb"
    elif (arg == "-t"):       #set test length
        arg = args.pop(0)
        TIME = "#" + arg + ";\n"
    elif (arg == "-i"):       #create the list of inputs
        while len(args) and not args[0].startswith('-'):
            arg = args.pop(0)
            INPUTLIST.append(arg)
    elif (arg == "-o"):     #create the list of outputs
        while len(args) and not args[0].startswith('-'):
            arg = args.pop(0)
            OUTPUTLIST.append(arg)
    elif (arg == "-si"):    #create the list of system inputs
        while len(args) and not args[0].startswith('-'):
            arg = args.pop(0)
            SYSTEMINPUTS.append(arg)
    elif (arg == "-so"):    #create the lit of system outputs
        SYSTEMOUTPUTS
        while len(args) and not args[0].startswith('-'):
            arg = args.pop(0)
            SYSTEMOUTPUTS.append(arg)
    elif (arg == "-bv"):     #create the list of test values
        if not len(INPUTLIST):
            raise RuntimeError("Inputs must be specified with the -i flag before values can be \
                                \npassed with the -bv flag.")
        
        valsPerTest = len(INPUTLIST)
        COMPTEST = False

        while len(args) and not args[0].startswith('-'): #creates a list containing lists containing
                                                         #the values to be tested in each test
            test = []
            while len(test) < valsPerTest:
                arg = args.pop(0)
                test.append(arg)
            TESTLIST.append(test)
    
    elif (arg == "-dv"): #create the list of test values with decimal inputs
        if not len(INPUTLIST):
            raise RuntimeError("Inputs must be specified with the -i flag before values can be \
                                \npassed with the -dv flag.")

        valsPerTest = len(INPUTLIST)
        COMPTEST = False

        while len(args) and not args[0].startswith('-'): #creates a list containing lists containing
                                                         #the values to be tested in each test
            test = []
            while len(test) < valsPerTest:
                arg = args.pop(0)
                arg = int(arg)
                arg = bin(arg)[2:]
                test.append(arg)
            TESTLIST.append(test)

    elif (arg == "-hv"): #create the list of test values with decimal inputs
        if not len(INPUTLIST):
            raise RuntimeError("Inputs must be specified with the -i flag before values can be \
                                \npassed with the -dv flag.")

        valsPerTest = len(INPUTLIST)
        COMPTEST = False

        while len(args) and not args[0].startswith('-'): #creates a list containing lists containing
                                                         #the values to be tested in each test
            test = []
            while len(test) < valsPerTest:
                arg = args.pop(0)
                arg = bin(int(arg, 16))[2:]
                test.append(arg)
            TESTLIST.append(test)

    else:
        raise RuntimeError("Invalid input.")

if INTERACTIVE == True:
    fileNameInput = input("Enter your desired testbench file name. Omit the extension. If you \
                           \nleave this blank, your testbench filename will be 'system.v': ")
    if fileNameInput != "":
        FILENAME = fileNameInput + "_tb"

    inputsInput = input("\nEnter your desired inputs, separated by spaces (these will be the \
                 \ninputs to the testbench). \
                 \nYou don't need to specify that they'll be listed as registers in the \
                 \ntestbench, but you do need to specify their size (e.g. [2:0]testA [3:0]testB): ")
    INPUTLIST = [str(x) for x in inputsInput.split()]

    outputsInput = input("\nEnter your desired outputs (formatted the same way as the inputs): ")
    OUTPUTLIST = [str(x) for x in outputsInput.split()]

    sInputsInput = input("\nEnter your desired UUT inputs, separated by spaces (these should \
                          \nbe the inputs to the unit under test). Size need not be specified: ")
    SYSTEMINPUTS = [str(x) for x in sInputsInput.split()]

    sOutputsInput =input("\nEnter your desired UUT outputs, formatted the same as the UUT inputs: ")
    SYSTEMOUTPUTS = [str(x) for x in sOutputsInput.split()]

    timeInput = input("\nEnter the desired length of each test, in ns. If you leave this blank, \
                       \n10 ns will be used: ")
    if (timeInput):
        TIME = "#" + timeInput + ";\n"

    compTest = input("\nDo you want to specify your test values, or should the program generate \
                      \na testbench testing all possible combinations of values? (y/n): ")
    if compTest == "y":
        COMPTEST = False
    if COMPTEST == False:
        base = input("\nDo you wish to use binary, decimal, or hexadecimal for your test values \
                      \n(b/d/h)? (Note choosing one here and using another format when specifying \
                      \nvalues will result in meaningless test values: ")
        values = input("\nEnter each value to be tested, separated by spaces. (for example, if \
                         \nyou want two tests, one with opcode = 1, testA = 0, and testB = 0, and \
                         \none with opcode = 1, testA = 1, and testB = 1, type '1 0 0 1 1 1'). \
                         \nNote that you do not need to specify the radix or the size in bits: ")
        valueList = [str(x) for x in values.split()]
        valsPerTest = len(INPUTLIST)
        numTests = len(valueList)

        while len(TESTLIST) < numTests / valsPerTest:
            test = []
            while len(test) < valsPerTest:
                arg = valueList.pop(0)
                if base == "d":
                    arg = int(arg)
                    arg = bin(arg)[2:]
                elif base == "h":
                    arg = bin(int(arg, 16))[2:]
                test.append(arg)
            TESTLIST.append(test)

#Main
outputFile = open(FILENAME + ".v", "w")
outputFile.write("`timescale 1ns/1ns\n\nmodule " + FILENAME + "();\n")

io(outputFile, INPUTLIST, OUTPUTLIST)
uut(outputFile, INPUTLIST, OUTPUTLIST, SYSTEMINPUTS, SYSTEMOUTPUTS, TESTLIST, TIME)
