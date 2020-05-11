

#XTD:xrisam00
import os
import sys
import re
from xml.dom import minidom
from xml.dom import Node
#enums
#error codes
ParamError,InputError,OutputError=range(1,4)
#data types
TBit,TInt,TFloat,TNvarchar,TNtext=range(0,5)
#help string
HELP='xtd.py [--help|g][-ab][--input=fname][--output=fname][--header="head"]'+"[--etc=n]\n"

'''############################################################################
CLASS TABLE
TABLENAME is string
LISTOFELEMENTANDTYPES is list of couples (collumn name,collumn type)
'''############################################################################
class Table:
    TableName = "tablename"
    ListOfElementsAndTypes = []
    #constructor
    def __init__(self,NameOfTable):
        self.TableName = NameOfTable
        self.ListOfElementsAndTypes = []
    #method prints to given stream table and its columns
    def print2DDL(self,OutputStream):
        #print table name and primary key of table
        OutputStream.write("CREATE TABLE "+self.TableName+"(\nprk_"+self.TableName
        +"_id INT PRIMARY KEY")
        #print columns and their type
        for element in self.ListOfElementsAndTypes:
            if(element[2]<2 and element[0] != "value"):
                OutputStream.write(",\n"+element[0]+"_id "+element[1])
            else:
                OutputStream.write(",\n"+element[0]+" "+element[1])
        #print ending mark of table definition
        OutputStream.write("\n);\n")
  #  def print2XML(self,XMLDoc):
'''############################################################################
Functions
'''############################################################################

#gets list of all element's names
def GetAllElementsFromNode(rootElement):
    result=[]
    ListOfChildNodes = rootElement.childNodes
    for node in ListOfChildNodes:
        if(node.nodeType != Node.TEXT_NODE):
            if(node.hasChildNodes() == True):
                result.extend(GetAllElementsFromNode(node))
            result.append(node.nodeName)
    return result

#returns data type of string attribute value
def GetAttributeType(string):
    if(string == ""):
        return "BIT"
    elif(re.match(r"^\s*True\s*$",string) or
        re.match(r"^\s*False\s*$",string) or
        re.match(r"^\s*0|1\s*$",string)
    ):
        return "BIT"
    elif(re.match(r"^\s*\d+\s*$",string)):
        return "INT"
    elif(re.match(r"^\s*\d+\.\d+\s*$",string)):
        return "FLOAT"
    elif(re.match(r"^\s*\d+\.\d+(e|E)\d+\s*$",string)):
        return "FLOAT"
    elif(re.match(r"^\s*\d+(e|E)\d+\s*$",string)):
        return "FLOAT"
    else:
        return "NVARCHAR"
def CheckDuplicates(ListOfTableObjects):
    for object in ListOfTableObjects:
        for element in object.ListOfElementsAndTypes:
            #for all attributes
            if(element[2] == 2):
                index=0
                for anotherelement in object.ListOfElementsAndTypes:
                    #for all text subelelements or foreing key
                    if element[0] == anotherelement[0] and element[2] != 2:
                        if(element[0]== "value" and anotherelement[2]==1):
                            if(element[1] == "NVARCHAR"):
                                if(anotherelement[1] =="NTEXT"):
                                    element[2]=anotherelement[2]
                                    element[1]=anotherelement[1]
                                    object.ListOfElementsAndTypes.pop(index)

                            else:
                                if(element[1]<anotherelement[1]):
                                    element[2]=anotherelement[2]
                                    element[1]=anotherelement[1]
                                    object.ListOfElementsAndTypes.pop(index)
                        else:
                            sys.exit(90)
                    index +=1
        for element in object.ListOfElementsAndTypes:
            #for all foreing key
            if(element[2] == 0):
                for anotherelement in object.ListOfElementsAndTypes:
                    #for all text subelelements
                    if element[0] == anotherelement[0] and element[2] != 0:
                        sys.exit(90)
#function corrects type of elemtents of ListoftableObjects
def CorrectType(ListOfTableObjects):
    for object in ListOfTableObjects:
        anotherindex=0
        for element in object.ListOfElementsAndTypes:
            index=0
            occurences = 0
            for anotherelem in object.ListOfElementsAndTypes:
                if anotherelem == element and anotherindex != index:
                    object.ListOfElementsAndTypes.pop(index)
                    occurences += 1
                elif anotherelem[0] == element[0] and anotherelem[1] < element[1]:
                    object.ListOfElementsAndTypes.pop(index)
                elif anotherelem[0] == element[0] and anotherelem[1] > element[1]:
                    object.ListOfElementsAndTypes.pop(anotherindex)

                index +=1
            anotherindex +=1
#function fill with data list of tables without attributes
def FillWithDataWithoutAttributes(ListOfTableObjects,indoc):
    #for each found table
    for object in ListOfTableObjects:
        #get list of its occurences
        list = indoc.getElementsByTagName(object.TableName)
        #search for text elements
        for el in list:
            for node in el.childNodes:
                if node.nodeType == Node.TEXT_NODE and node.data != "" and not re.match(r"\s+",node.data):
                    #    nodename  nodetype                     type of record
                    temp=["value",GetTextElementType(node.data),1]
                    if temp not in object.ListOfElementsAndTypes:
                        object.ListOfElementsAndTypes.append(temp)

        #search for foreing keys
        for node in list:
            for child in node.childNodes:
                if(child.nodeType == Node.ELEMENT_NODE):
                    temp=[child.nodeName,"INT",0]
                    if temp not in object.ListOfElementsAndTypes:
                        object.ListOfElementsAndTypes.append(temp)

def CountMaxSon(parentName,nodeName,indoc):
    max_occurences=0;
    list = indoc.getElementsByTagName(parentName)
    for node in list:
        occurence=0
        for child in node.childNodes:
            if(child.nodeName==nodeName):
                occurence+=1
        if(occurence > max_occurences):
            max_occurences = occurence
    return max_occurences

#function fill with data list of tables
def FillWithData(ListOfTableObjects,indoc):
    #for each found table
    for object in ListOfTableObjects:
        #get list of its occurences
        list = indoc.getElementsByTagName(object.TableName)
        #search for text elements
        for el in list:
            for node in el.childNodes:
                if node.nodeType == Node.TEXT_NODE and node.data != "" and not re.match(r"\s+",node.data):
                    #    nodename  nodetype                     type of record
                    temp=["value",GetTextElementType(node.data),1]
                    if temp not in object.ListOfElementsAndTypes:
                        object.ListOfElementsAndTypes.append(temp)


        #search for attributes
        for attr in list:
            if (attr.hasAttributes() == True):
                for nod in range (0,attr.attributes.length):
                    temp=[str(attr.attributes.item(nod).name),GetAttributeType(attr.attributes.item(nod).value),2]
                    if temp not in object.ListOfElementsAndTypes:
                        object.ListOfElementsAndTypes.append(temp)

        #search for foreing keys
        for node in list:
            for child in node.childNodes:
                if(child.nodeType == Node.ELEMENT_NODE):
                    temp=[child.nodeName,"INT",0]
                    if temp not in object.ListOfElementsAndTypes:
                        object.ListOfElementsAndTypes.append(temp)
def RemoveLowerTypesAtSameNamespace(ListOfTableObjects):
    for object in ListOfTableObjects:
        anotherindex=0
        for element in object.ListOfElementsAndTypes:
            index=0
            for anotherelement in object.ListOfElementsAndTypes:
                if(element[0]==anotherelement[0] and index != anotherindex):
                    if(element[1]== "NVARCHAR"):
                        if anotherelement[1]== "NTEXT":
                            element[1] = "NTEXT"
                    else:
                        if anotherelement[1] > element[1]:
                            element[1] = anotherelement[1]
                            element[2] = anotherelement[2]

                index +=1
            anotherindex+=1




#returns data type of text element value
def GetTextElementType(string):
    if(string == ""):
        return "BIT"
    elif(re.match(r"^\s*True\s*$",string) or
        re.match(r"^\s*False\s*$",string) or
        re.match(r"^\s*0|1\s*$",string)
    ):
        return "BIT"
    elif(re.match(r"^\s*\d+\s*$",string)):
        return "INT"
    elif(re.match(r"^\s*\d+\.\d+\s*$",string)):
        return "FLOAT"
    elif(re.match(r"^\s*\d+\.\d+(e|E)\d+\s*$",string)):
        return "FLOAT"
    elif(re.match(r"^\s*\d+(e|E)\d+\s*$",string)):
        return "FLOAT"
    else:
        return "NTEXT"
'''############################################################################
MAIN SCRIPT
'''############################################################################
#stream variables
ins = sys.stdin
outs = sys.stdout
#parsing command line arguments
#counter for each command line argument
param_help=0
param_input_file=0
param_output_file=0
param_header=0
param_etc=0
param_noattributes=0
param_nosubelements=0
param_xmloutput=0
#data for command line arguments
etc=0
input_file=""
outut_file=""
header=""
#loop through command line arguments and count occurences of them
#if unrecognized argument appears script returns exit code 1
for arg in sys.argv:
    if(arg == "--help"):
        param_help+=1
    elif re.match(r"^--input=",arg):
        param_input_file+=1
        input_file = re.sub("^--input=", "",arg)
    elif re.match(r"^--output=",arg):
        param_output_file+=1
        outut_file = re.sub("^--output=", "",arg)
    elif re.match(r"^--header=",arg):
        param_header+=1
        header = re.sub("^--header=", "",arg)
    elif re.match(r"^--etc=",arg):
        param_etc+=1
        etc = re.sub("^--etc=", "",arg)
    elif (arg == "-a"):
        param_noattributes+=1
    elif (arg == "-b"):
        param_nosubelements+=1
    elif (arg == "-g"):
        param_xmloutput+=1
    else:
        if (arg != sys.argv[0]):
            sys.stderr.write(HELP)
            exit(ParamError)

#if there was any command line argument set multiple times
if (param_etc > 1 or param_header > 1 or param_help > 1 or param_input_file > 1
    or param_noattributes > 1 or param_nosubelements > 1 or param_output_file >1
    or param_xmloutput > 1):
    sys.stderr.write("too many arguments\n"+HELP)
    exit(ParamError)

#if exclusive command line arguments were set
if((param_nosubelements == param_etc and param_etc == 1) or
(param_xmloutput == 1 and param_help == 1)):
    sys.stderr.write("exclusive arguments set\n"+HELP)
    exit(ParamError)

#if help needs to be printed
if(param_help == 1):
    sys.stdout.write(HELP)
    exit(0)

#open input file if needed
if(param_input_file == 1):
    try:
        ins = open(input_file,"r")
    except IOError:
        sys.stderr.write("unable to open input file:"+input_file+"\n")
        exit(InputError)
    #parse input xml file to internal minidom specification
    indoc = minidom.parse(ins)
else:
    string=''
    line = ins.readline()
    while line:
        string = string + line
        line = ins.readline()
    indoc = minidom.parseString(string)

#open output file if needed
if(param_output_file == 1):
    try:
        outs = open(outut_file,"w")
    except IOError:
        sys.stderr.write("unable to open output file\n")
        exit(OutputError)
'''############################################################################
PROCCESSING XML INPUT
'''############################################################################


#get list of all tables
TableNames = GetAllElementsFromNode(indoc.documentElement)
#remove duplicates
TableNames = list(set(TableNames))

ListOfTableObjects = []

#constructing list of table objects
for tablename in TableNames:
    ListOfTableObjects.append(Table(tablename))
#tesing###################################################################
if param_noattributes == 1:
    FillWithDataWithoutAttributes(ListOfTableObjects,indoc)
else:
    FillWithData(ListOfTableObjects,indoc)
#correct types in all tables
CorrectType(ListOfTableObjects)
#check for same names of values for attribtes or text atributes or elements exits 90
CheckDuplicates(ListOfTableObjects)
if(param_nosubelements == 1):
    RemoveLowerTypesAtSameNamespace(ListOfTableObjects)
else:
    for object in ListOfTableObjects:
        index=0
        for element in object.ListOfElementsAndTypes:
            iterate = CountMaxSon(object.TableName,element[0],indoc)
            print("counted"+ str(iterate))
            if param_etc == 1:
                if int(etc) < 0:
                    exit(ParamError)
                if int(etc) < iterate:

                    #find table with name element[0] and add relation if it does not exisst
                    for aobject in ListOfTableObjects:
                        if aobject.TableName == element[0]:
                            temp =[object.TableName,"INT",0]
                            if temp not in aobject.ListOfElementsAndTypes:
                                print("-------------------------"+aobject.TableName+object.TableName+"etc = "+str(etc)+":iterate"+str(iterate))
                                aobject.ListOfElementsAndTypes.append(temp)
                                object.ListOfElementsAndTypes.pop(index)
                else:
                    iterate+=1
                    for i in range (2,iterate):
                        object.ListOfElementsAndTypes.append([str(element[0])+str(i),element[1],element[2]])
                    if iterate > 2:
                        element[0] = element[0]+"1"
            else:
                iterate+=1
                for i in range (2,iterate):
                    object.ListOfElementsAndTypes.append([str(element[0])+str(i),element[1],element[2]])
                if iterate > 2:
                    element[0] = element[0]+"1"
            index+=1

if(param_header == 1):
    header = re.sub(r"^\'","",header)
    header = re.sub(r"^\"","",header)
    header = re.sub(r"\"&","",header)
    header = re.sub(r"\'","",header)
    outs.write("--"+header+"\n\n")
for object in ListOfTableObjects:
    object.print2DDL(outs)
'''############################################################################
ENDING PROCCESSING
'''############################################################################
#close input file if needed
if(param_input_file == 1):
    ins.close()
#close output file if needed
if(param_output_file == 1):
    outs.close()
exit(0)