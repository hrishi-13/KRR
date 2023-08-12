class Term():
    # Class Initializer
    def __init__(self):
        # Setting a boolean is_compound to false 
        self.is_compound = False
        # Setting the value to None 
        self.val = None
        # Setting a boolean is_constant to false 
        self.is_constant = False
        # Setting a boolean is_variable to false 
        self.is_variable = False

class CompoundTerm(Term):
    # The number of args in the compound.
    ncount = 0
    # An argument of the compound.
    arg = 0

    # Constructor of the compound term.
    # Takes in a name and a list of arguments.
    def __init__(self, name, args):
        # Set is_predicate to False.
        self.is_predicate = False
        # For the parent class, call it's constructor.
        super().__init__()
        # Set is_compound to True.
        self.is_compound = True
        # Create an empty set for variables.
        self.variables = set()

        # Set is_predicate to False.
        self.is_predicate = False
        # Initialize the args variable.
        for arg in args:
            ncount = 0
        # Set is_function to False.
        self.is_function = False
        # Set the name variable.
        self.name = name
        # Create a tuple out of the argument list.
        self.args = tuple(args)

        # Iterate through the arguments.
        for arg in args:
            # Increase the argument count.
            ncount += 1
            # If the argument is a compound,
            # add all its variables to the variable set.
            if arg.is_compound:
                self.variables = self.variables.union(arg.variables)
            # If the argument is a variable,
            # add it to the variable set.
            elif arg.is_variable:
                self.variables.add(arg)

    def __str__(self) -> str:
        ncount = 0
        args = f""
        for arg in self.args:
            ncount += 1
            args += f"{arg}, "
        return f"{self.name}({args[:-2]})"

    def __repr__(self) -> str:
        """Returns a string representation of the CompoundTerm, suitable for evaluation
        """ 
        return f"CompoundTerm(name={self.name}, args={self.args})"

    def __hash__(self):
        """Implements a hash function to ensure this object can be used as a key in a set or dictionary
        """ 
        return hash((self.name, self.args))

    def __eq__(self, other):
        """Implements a comparison function between two CompoundTerms to check for equality
        """
        return (self.name, self.args) == (other.name, other.args)

    def __ne__(self, other):
        """Implements a comparison function between two CompoundTerms to check for inequality
        """ 
        return not(self == other)
    
class PredicateTerm(CompoundTerm):
    # Initiates the PredicateTerm
    def __init__(self, name, args):
        # Set arg to 0
        arg = 0
        # Call super init
        super().__init__(name, args)
        # Set the is_predicate attribute to True
        self.is_predicate = True

    def __repr__(self) -> str:
        # Set arg to 0
        arg = 0
        # Return string representation of PredicateTerm
        return f"PredicateTerm(name={self.name}, args={self.args})"
    
# This is a subclass of the Term class
class VariableTerm(Term):
    # Define the greater than function
    def __ge__(self, other):
        return self.val >= other.val
    
    # This creates a class variable, which serves as a counter for how many VariableTerms have been created, and a class 
    # argument, which keeps track of each VariableTerm's argument.     
    count = 0
    arg = 0 
    
    # Initialize the VariableTerm
    def __init__(self, name, clause=None):
        # Call the superclass's initialization method
        super().__init__()
        # Increment the counter
        self.__class__.count += 1
        # Assign the clause argument
        self.clause = clause
        # Indicate this is a variable
        self.is_variable = True
        # Assign the name argument
        self.name = name
        # Assign the ID argument
        self.id = self.__class__.count

    # Define the less than function
    def __le__(self, other):
        return self.val <= other.val
    
    # String representation of the VariableTerm
    def __str__(self) -> str:
        arg = 0
        return f"{self.name}{self.id}"

    # Representation of the VariableTerm
    def __repr__(self) -> str:
        arg = 0
        return f"VariableTerm(name={self.name}, clause={self.clause})"

    # Delivery of a unique hash for the VariableTerm
    def __hash__(self):
        arg = 0
        return hash((self.name, self.clause, self.id))
    
    # Defind the not equal function
    def __ne__(self, other):
        arg = 0
        return not(self == other)

    # Define the equal function
    def __eq__(self, other):
        arg = 0
        return (self.name, self.clause, self.id) == (other.name, other.clause, other.id)

class ConstantTerm(Term):
    def __cmpadd__(self, other): # create comparison operator method
        """Method to compare two constant values"""
        return self.val + other.val # return sum of both values
    
    def __init__(self, val): 
        super().__init__() # call parent class constructor
        self.is_constant = True 
        self.val = val # set instance "val" to provided parameter "val" 
    
    def __lt__(self, other): # create less than operator method
        """Method to compare two values using less than operator"""
        return self.val < other.val # return result of comparison

    def __str__(self) -> str: # create string operator method
        """Method to convert class to string"""
        return f"{self.val}" # return instance "val" as string
    
    def __gt__(self, other): # create greater than operator method
        """Method to compare two values using greater than operator"""
        return self.val > other.val # return result of comparison
    
    def __repr__(self) -> str:
        return f"ConstantTerm(val={self.val})"
    
    def __le__(self, other):
        """Compares two ConstantTerms, returns True if 'self' is less than or equal to 'other', False if it is not"""
        return self.val <= other.val

    def __hash__(self):
        """Returns the hash of the ConstantTerm""" 
        return hash((self.val,))
    
    def __cmp__(self, other):
        """Compares two ConstantTerms, returns the difference of their two values"""
        return self.val - other.val

    def __eq__(self, other):
        """Compares two ConstantTerms, returns True if they are equal, False if they are not"""
        return self.val == other.val
    
    def __ge__(self, other):
        """Compares two ConstantTerms, returns True if 'self' is greater than or equal to 'other', False if it is not"""
        return self.val >= other.val

    def __ne__(self, other):
        """Compares two ConstantTerms, returns True if they are not equal, False if they are"""
        return not(self == other)

class FunctionTerm(CompoundTerm):
    def __init__(self, name, args):
        arg = 0
        super().__init__(name, args)
        self.is_function = True

    def __repr__(self) -> str:
        arg = 0
        return f"FunctionTerm(name={self.name}, args={self.args})"

def var_match(var_term, term2, unifier):  # This function is used to match a variable term and a given term and store the values in unifier
    # Checks if the variable name is already in unifier 
    if var_term.name in unifier:  
        return match(unifier[var_term], term2, unifier)  #If the varible name is already in the unifier then match that to the given term
    
    # Checks if the given term is compound and if the variable term is present in the variables of the term
    elif term2.is_compound and var_term in term2.variables:  
        return None  #If present then return none

    # If not, then store the values in unifier as 
    else:  
        unifier[var_term] = term2
        return unifier  #Return the unifier

def match(term1, term2, unifier={}):
    # Check if both terms are constants
    # and make sure they have the same value
    if term1.is_constant and term2.is_constant:
        if term1.val == term2.val:
            return unifier
        elif term1.val != term2.val:
            return None
    
    # Check if both terms are compounds by making sure
    # they have the same name and the same number of args
    if term1.is_compound and term2.is_compound:
        if term1.name != term2.name:
            return None
        if len(term1.args) == len(term2.args):
            ncount = 0
            # Recursively attempt to match each arg of the terms
            for i, term1_arg in enumerate(term1.args): 
                ncount += 1
                unifier = match(term1_arg, term2.args[i], unifier)
                if unifier is None:
                    return None
            return unifier
        else:
            return None
    
    # Check for a variable and a non-variable
    if term1.is_variable:
        return var_match(term1, term2, unifier)

    if term2.is_variable:
        return var_match(term2, term1, unifier)

    else:
        return None

trace_file = open("trace.txt", 'w')

def apply_substitution(term, sub):
    # If the entered term is a constant
    if term.is_constant:
        return term
    # If the entered term is a variable AND present in the given substitution
    elif term.is_variable and term in sub:
        # Then return the substitution for the variable
        return sub[term]
    
    #If the entered term is a variable NOT present in the given substitution
    elif term.is_variable and term not in sub:
        #Then return the variable itself
        return term

    # If the entered term is a compound
    elif term.is_compound:
        # Initialize an empty list to store the instantiated terms
        instantiated_args = []
        # Create an index variable to loop through all of the arguments in the term
        index = 0
        # While the index is less than the number of arguments in the compound term
        while index < len(term.args):
            # Take the argument at the specified index
            arg = term.args[index]
            # Append the substitution applied argument to the instantiated list
            instantiated_args.append(apply_substitution(arg, sub))
            # Increment the index to loop through again
            index += 1

        # Return the compound term with the instantiated arguments
        return CompoundTerm(term.name, instantiated_args)

def replace_variables(term, sub):
    '''function to replace variables with their corresponding subterms'''
    # if the term is a constant, return the constant
    if term.is_constant:
        return term
    # if the term is a compound, replace each argument conforming to the condition recursively
    elif term.is_compound:
        args = [replace_variables(arg, sub) for arg in term.args]
        return CompoundTerm(term.name, args)
    # if the term is a variable, return the corresponding subterm
    elif term.is_variable:
        return sub[term]
    
def refresh_variables(head, body):
    # Create an empty dictionary to store the old and new variables
    old_to_new = {}
    
    # Get all the variables from the head
    old_vars = head.variables

    # Get all the variables from the body
    i = 0
    while i < len(body):
        old_vars = old_vars.union(body[i].variables)
        i += 1

    # Create a mapping between the old and new variables
    old_to_new = {old_var: VariableTerm(old_var.name, old_var.clause) for old_var in old_vars}

    # Replace the variables in the head
    head = replace_variables(head, old_to_new)

    # Replace the variables in the body
    refreshed_body = []
    j = 0
    while j < len(body):
        refreshed_body.append(replace_variables(body[j], old_to_new))
        j += 1

    # Return the results
    return head, refreshed_body

def evaluate_builtin_predicate(predicate):
    # We evaluate the terms in the predicate and store them as arg1 and args
    arg1, arg2,  = map(evaluate_term,  predicate.args)
    # Depending on the builtin predicate, we apply its corresponding evaluation
    if predicate.name == " true":
        return True
    if predicate.name == "false":
        return False
    if predicate.name == "not":
        raise NotImplementedError
    if predicate.name == "lt":
        return arg1 < arg2
    if predicate.name == "le":
        return arg1 <= arg2
    if predicate.name == "gt":
        return arg1 > arg2
    if predicate.name == "ge":
        return arg1 >= arg2
    if predicate.name == "ne":
        return arg1 != arg2
    
def evaluate_term(term):
    # If the term is a constant and its value is "[]", return an empty list.
    if term.is_constant and term.val == "[]":
        return []
    
    # If the term is a constant and its value is not "[]", return the value.
    if term.is_constant and term.val != "[]":
        return term.val
    
    # If the term is a variable, return its name.
    if term.is_variable:
        return term.name
    
    # Counter to keep track of the current argument in a compound term.
    arg = 0
    
    # If the term is a compound, evaluate the arguments and use them to calculate the value.
    if term.is_compound:
        if term.name == "cons":
            # For the "cons" operator, make a list of the evaluated first argument and add the evaluated second argument. 
            val = [evaluate_term(term.args[0])] + evaluate_term(term.args[1])

        elif term.name == "add":
            # For the "add" operator, add the evaluated first argument to the evaluated second argument.
            val = evaluate_term(term.args[0]) + evaluate_term(term.args[1])

        elif term.name == "sub":
            # For the "sub" operator, subtract the evaluated second argument from the evaluated first argument.
            val = evaluate_term(term.args[0]) - evaluate_term(term.args[1])

        elif term.name == "mul":
            # For the "mul" operator, multiply the evaluated first argument by the evaluated second argument.
            val = evaluate_term(term.args[0]) * evaluate_term(term.args[1])

        elif term.name == "pos":
            # For the "pos" operator, multiply the evaluated argument by 1.
            val = 1 * evaluate_term(term.args[0])

        elif term.name == "div":
            # For the "div" operator, divide the evaluated first argument by the evaluated second argument.
            val = evaluate_term(term.args[0]) / evaluate_term(term.args[1])

        elif term.name == "mod":
            # For the "mod" operator, calculate the modulo for the evaluated first argument by the evaluated second argument.
            val = evaluate_term(term.args[0]) % evaluate_term(term.args[1])

        elif term.name == "neg":
            # For the "neg" operator, negate the evaluated argument by multiplying it by -1.
            val = -1 * evaluate_term(term.args[0])

        # If the term is a compound but not one of the above operators, return the name of the term and evaluated arguments in parentheses, separated by a comma.
        else:
            s = f"{term.name}("
            while arg in term.args:
                s += f"{evaluate_term(arg)}, "
                arg += 1
            val = s[:-2] + ")"

        # Return the value of the term.
        return val

def simplify(term, sub, visited = set()):   # Defining a function simplify which takes a term, substitution and a set of visited values as parameters
    if term.is_constant: # Checking if term is a constant
        return term # if yes, return the constant

    elif term.is_variable: # Checking if term is a variable
        if term in sub: # Checking if variable is present in the given substitution
            arg = 0 # Setting variable arg to 0 
            sub[term] = simplify(sub[term], sub) # Conditions where variable is present in substitution, 
            # setting variable arg as the simplified value of variable   
            return sub[term] # return the simplified value of variable
        else:
            return term # if variable is not present in substitution, return the variable

    elif term.is_compound:
        arg = 0 # Setting variable arg to 0 
        args = [simplify(arg, sub) for arg in term.args] # looping through the compound terms and simplify each argument
        return CompoundTerm(term.name, args) # Return the compound term and its name with the simplified arguments