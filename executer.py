import sys
import argparse
import xml.etree.ElementTree as ElTree
from supports import *
from supports import ConstantTerm, FunctionTerm, VariableTerm, PredicateTerm, evaluate_builtin_predicate, simplify, evaluate_term, apply_substitution, refresh_variables, match, trace_file
from inspect import trace
from copy import deepcopy

def solve_goals(kb, goals, mgu={}, cut_scope = False, depth=0):
    solved = False
    ''' check if the list of goals is empty or not '''
    if goals:
        goal = goals[0]
        print(f"Depth: {depth}\nSolving goal: {goal}", file=trace_file)

        ''' if the goal is in built-in predicates, evaluate the built-in predicate else proceed'''
        if goal.name in INBUILT_PREDICATES_LOWER:
            if not evaluate_builtin_predicate(goal):
                print("Returned False!\n", file=trace_file)
                return False  
            else:
                return solve_goals(kb, goals[1:], mgu, cut_scope, depth + 1)

        ''' check the goal name is "cut" '''
        if goal.name == "cut":
            solve_goals(kb, goals[1:], mgu, False, depth + 1)
            return True

        ''' if the goal name is "not", if solve_goals returns true then return false, else move to goals[1:] '''
        if goal.name == "not":
            if solve_goals(kb, goal.args, mgu, cut_scope, depth + 1):
                return False
            else:
                return solve_goals(kb, goals[1:], mgu, cut_scope, depth + 1)
            
        # This loop will iterate until the goal is solved or the cut_scope is true.
        for i, head in enumerate(kb):
            if solved:
                if cut_scope:
                    break

            # refreshes the variables in the head and the head's corresponding body clauses
            head, body = refresh_variables(head, kb[head])

            # attempts to match the current goal with the head atom
            unifier = match(goal, head, deepcopy(mgu))

            if unifier is not None:
                # writes to trace file
                print(f"Depth: {depth}\ngoal: {goal}\nmatch: {head}", file=trace_file)

                s = (f"Unifier:\n")

                # checks to see if "cut" appears in the body
                for g in body:
                    if g.name == "cut":
                        cut_scope = True

                # writes to trace file
                for k, v in unifier.items():
                    s += f"{k} :{v}\n"
                print(f"{s}\n", file=trace_file)

                # updates the goals list with the goals from the head's body, applying the unifier
                updated_goals = body + goals[1:]
                updated_goals = [apply_substitution(g, unifier) for g in updated_goals]

                # if there are goals remaining, write to trace file
                if not updated_goals:
                    s = ("All Goals Solved!!\n")                    
                else:
                    s = ("NEW GOALS:\n")
                    for g in updated_goals:
                        s += str(g) + "\n"

                # writes to trace file 
                print(f"{s}\n", file=trace_file)

                # recursively call solve_goals with the new updated goals and the new unifier with increased depth
                if solve_goals(kb, updated_goals, unifier, cut_scope, depth + 1):
                    solved = True
            else:
                # if the goal could not be matched, continue to the next head in the loop 
                continue

        # if the goal was not solved, write to trace file 
        if not solved:
            print("Failed to match Goal!", file=trace_file)

    else:
        variables_present = False
        s = (f"MGU:\n")
        # iterating mgu items
        for v in mgu:
            variable_not_used = True       
        for k, v in mgu.items():
            s += f"{k} : {v}\n"
        print(f"{s}\n", file=trace_file)
         

        variables_present = any(v.clause == 'q' for v in mgu)
        if variables_present:
            # iterates through each variable in the mgu
            for v in mgu:
                # checks if the clause is 'q'
                if v.clause == 'q':
                    simplified_val = simplify(v, mgu)
                    print(f"{v.name} = {evaluate_term(simplified_val)}", file=trace_file)
                    print(f"{v.name} = {evaluate_term(simplified_val)}")
                    
        # if variables are not present in the mgu
        if not variables_present:
            print("True")
            print("True", file=trace_file)
            sys.exit(0)

        # prompt user to look for more solutions 
        explore_more = input("Enter c to look for more solutions:").upper()
        
        # if the user does not want to look for more solutions
        if explore_more != "C":
            sys.exit(0)
        else:
             # prints to trace_file that user chose to continue
            print("User chose to continue", file=trace_file)
            solved = True
            

    return solved

INBUILT_PREDICATES = {"LT", "LE", "EQ", "GE", "GT", "NE", "NOT", "FALSE", "TRUE", "CUT"}
INBUILT_PREDICATES_LOWER = {s.lower() for s in INBUILT_PREDICATES}
INBUILT_PREDICATES_LOWER.remove("eq")
INBUILT_FUNCTIONS = {"CONS", "NEG", "ADD", "SUB", "MUL", "DIV", "MOD"}
INBUILT_FUNCTIONS_LOWER = {s.lower() for s in INBUILT_FUNCTIONS}

def parse_function(fn, variable_terms, clause_num):
    # a list of arguments of the function, which can be ConstantTerm, VariableTerm, or FunctionTerm objects
    arg_terms = [] 
    for arg in fn:  # for each argument of the function
        if arg.tag == "CONSTANT":  
            arg_terms.append(ConstantTerm(val=arg.text))  

        if arg.tag == "INTEGER":  # if the argument is an integer (number)
            arg_terms.append(ConstantTerm(val=int(arg.text)))  # then create a ConstantTerm object with the integer value

        if arg.tag == "VARIABLE":  # if the argument is a variable (string preceded with a capital letter)
            if arg.text in variable_terms:  
                arg_terms.append(variable_terms[arg.text])  

        if arg.tag == "NIL":  # if the argument is the empty list
            arg_terms.append(ConstantTerm(val='[]')) 

        if arg.tag in INBUILT_FUNCTIONS:  # if the argument is a builtin function (CONS, NEG, ADD, SUB, MUL, DIV, MOD)
            arg.attrib["name"] = arg.tag.lower()  
            arg_terms.append(parse_function(arg, variable_terms, clause_num))  # call the parse_function() function recursively with the argument

        if arg.tag == "FUNCTION":  # if the argument is a function (non-builtin)
            arg_terms.append(parse_function(arg, variable_terms, clause_num))  # call the parse_function() function recursively with the argument

    return FunctionTerm(name=fn.attrib["name"], args=arg_terms)  # create a FunctionTerm object and return it

# Parse_Predicate() is a helper function to parse Predicate XML Tags and create Predicate Term mappings.
# This function takes 3 parameters which are Predicate, Variable_Terms and Clause_Num.

def parse_predicate(predicate, variable_terms={}, clause_num=None):
    variables = collect_variables(predicate)

    # For each variable in the PREDICATE, if it is not in the Variable_Terms map, then create a new VariableTerm using the Clause_Num.
    for v in variables:
        variable_terms.setdefault(v, VariableTerm(v, clause_num))

    
    # If the predicate tag is inbuilt, then update the name attribute to lowercase.
    if predicate.tag in INBUILT_PREDICATES:
        predicate.attrib["name"] = predicate.tag.lower()

    # If the PREDICATE tag is a NOT tag, then parse the argument and return a PredicateTerm with "not" as its name and the argument as its argument.

    elif predicate.tag == "NOT":
        arg, = predicate
        return PredicateTerm("not", args=[parse_predicate(arg)])

    # Create a list of Argument Terms which will be added into the  PREDICATE Term as its argument.
    arg_terms = []
    for arg in predicate:
        # If the argument tag is constant, then create a ConstantTerm with the attribute of its text value.
        if arg.tag == "CONSTANT":
            arg_terms.append(ConstantTerm(val=arg.text))

        # If the argument tag is Integer, then create a ConstantTerm with the attribute of its text value as an Integer.
        if arg.tag == "INTEGER":
            arg_terms.append(ConstantTerm(val=int(arg.text)))

        # If the argument tag is Variable, then check if it exists in the Variable_Terms map. If it does, append it to the arg_terms list.
        if arg.tag == "VARIABLE":
            if arg.text in variable_terms:
                arg_terms.append(variable_terms[arg.text])

        # If the argument tag is NIL, then create a ConstantTerm with the val of "[]".
        if arg.tag == "NIL":
            arg_terms.append(ConstantTerm(val='[]'))

        # If the argument tag is an inbuilt function, then update the name attribute to lowercase.
        if arg.tag in INBUILT_FUNCTIONS:
            arg.attrib["name"] = arg.tag.lower()
            arg_terms.append(parse_function(arg, variable_terms, clause_num))

        # If the argument tag is a FUNCTION, then parse the function and append it to the arg_terms.
        if arg.tag == "FUNCTION":
            arg_terms.append(parse_function(arg, variable_terms, clause_num))

        # If the argument tag is none of the above then throw an error and exit the program.
        

    # Once all the argument terms have been parsed, create a PredicateTerm with the Predicate tag's name and the argument terms list as arguments. 
    return PredicateTerm(name=predicate.attrib["name"], args=arg_terms)

def collect_variables(predicate):
    # Create a set to store the variables
    variables = set()

    # Loop through every instance of the VARIABLE tag in the passed predicate  
    for v in predicate.iter('VARIABLE'):
       # Add the variable text to set
       variables.add(v.text)

    # Return all collected variables
    return variables

def parse_rule(rule, count):
    # Create a set to store the variables
    variables = set()

    # Create a dictionary to hold the mapping of variables to VariableTerm objects
    variable_terms = {}

    # Loop through every goal in the rule
    for goal in rule:
        # add any new variables found to the set
        variables = variables.union(collect_variables(goal))

    # Create an array to store all of the "body" predicates
    body = []

    for v in variables:
        # Create a VariableTerm for each of the variables and add it to the dictionary
        variable_terms[v] = VariableTerm(v, count)

    # Parse the first predicate in the rule, which will become the "head"
    head = parse_predicate(rule[0], variable_terms, count)

    # loop through the rest of the predicates in the rule
    for goal in rule[1:]:
        # Add each of the parsed predicates to the body array
        body.append(parse_predicate(goal, variable_terms, count))

    # return the head and body predicates
    return head, body

def parse_query(file):
    """Takes an XML query file and parses it into a list of goals"""
    # Create an ElementTree object to parse the file
    tree = ElTree.parse(file)
    # Get the root of the tree
    kb = {}
    query = tree.getroot()[0]
    # Extract the head and body of the query
    program = tree.getroot()
    head, body = parse_rule(query, 'q')
    # Create a list of goals 
    goals = [head] + body
    # Return the goals 
    return goals

def parse_KB(file):
    """Takes an XML file and parses it into a knowledge base by extracting facts and rules"""
    # Create an empty dictionary to hold the facts and rules
    kb = {}
    # Create an ElementTree object to parse the file
    tree = ElTree.parse(file)
    # Get the root of the tree
    program = tree.getroot()
   
    # Iterate over the tree and extract facts and rules
    for i, clause in enumerate(program):
        i += 1
        # If the clause is a rule
        if clause.tag == "RULE":
            # Extract the head and body of the rule
            head, body = parse_rule(clause, i)
            # Add the rule to the dictionary
            kb[head] = body
    
        # If the clause is a fact
        elif clause.tag == "FACT":
            # Extract the predicate of the fact
            fact = parse_predicate(clause[0], clause_num=i)
            # Add the fact to the dictionary
            kb[fact] = []

    # Return the knowledge base represented as a dictionary
    return kb

#parsing the arguments given to the program
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--knowledgebase', help='Uses clauses from this file to construct the KB', required=True)
parser.add_argument('-q', '--query', help='Query is taken from this file', required=True)
args = parser.parse_args()

#function to solve the set of goals recursively
def main():
    # parse the knowledge base 
    knowledgebase = parse_KB(args.knowledgebase)
    print("Finished Parsing the KB", file = trace_file)
    # parsing the query
    query = parse_query(args.query)
    print("Finished Parsing the QUERY", file = trace_file)
    s = ("Query:\n")

    # adding queries to the string
    s = ""
    i = 0
    while i < len(query):
        s += str(query[i]) + "\n"
        i += 1

    # printing the queries
    print(f"{s}\n", file=trace_file)
    print(f"{s}\n")

    # adding built in predicates
    knowledgebase.update(builtin_predicates_adding(knowledgebase))

    #solving the goals
    output = solve_goals(knowledgebase, query)
    print(output)
    print(output, file = trace_file)

# helper function to add the built in predicates
def builtin_predicates_adding(knowledgebase):
    numc = len(knowledgebase)
    numi = 0
    numc += 1
    arg = VariableTerm(name = 'X', clause = numc)
    numi += 1
    head = PredicateTerm(name = "eq", args = [arg, arg])
    return {head: []}

# main function
if __name__ == "__main__":
    main()

# closing the trace_file
trace_file.close()