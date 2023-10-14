from intbase import *
from brewparse import *

# TODO CASES I STILL NEED TO COVER
# calling print inside an expression vs a statement
# calling inputi with int + string

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)   # call InterpreterBase's constructor

    
    def run(self, program):
        ast = parse_program(program)
        self.variable_name_to_value = {}
        main_node = self.get_main_node(ast)
        self.run_function(main_node)
        
        
    def get_main_node(self, ast):
        for function in ast.dict["functions"]:
            if function.dict['name'] == "main":
                return function
        super().error(
            ErrorType.NAME_ERROR,
            "Main function not found",
        )
    
    def run_function(self, function_node):
        for statement_node in function_node.dict['statements']:
            self.run_statement(statement_node)
    
    def run_statement(self, statement_node):
        if self.is_assignment(statement_node):
            self.do_assignment(statement_node)
        if self.is_function(statement_node):
            self.do_function(statement_node)
    
    def do_assignment(self, statement_node):
        variable_name = self.get_variable_name(statement_node)
        source_node = self.get_expression(statement_node)
        resulting_value = self.evaluate_expression(source_node)
        self.variable_name_to_value[variable_name] = resulting_value
    
    def do_function(self, statement_node):
        function_name = statement_node.dict['name']

        match function_name:
            case 'print':
                self.do_print(statement_node)
            case 'inputi':
                return self.do_input(statement_node)
            case _:
                super().error(
                    ErrorType.NAME_ERROR,
                    "Unknown function call",
                )
    
    def do_print(self, print_statement_node):
        # returns a list of arguments that have been evaluated
        arguments_to_print = self.get_arguments_to_print(print_statement_node)

        string_to_output = ''

        # concatenate without spaces into a string
        for argument in arguments_to_print:
           string_to_output += str(argument)
        
        super().output(string_to_output)
    
    def do_input(self, input_statement_node):
        if len(input_statement_node.dict['args']) == 1:
            prompt = input_statement_node.dict['args'][0].dict['val']
            super().output(prompt)

        if len(input_statement_node.dict['args']) > 1:
            super().error(
                ErrorType.NAME_ERROR,
                "No inputi() function found that takes > 1 parameter",
            )
        
        user_input = int(super().get_input())

        return user_input

    def is_function(self, statement_node):
        return statement_node.elem_type == 'fcall'
    def is_assignment(self, statement_node):
        return statement_node.elem_type == '='
    def is_operation(self, source_node):
        return source_node.elem_type == '+' or source_node.elem_type == '-'
    def is_variable(self, source_node):
        return source_node.elem_type == 'var'
    def is_value(self, source_node):
        return source_node.elem_type == 'int' or source_node.elem_type == 'string'
    def is_int(self, source_node):
        return source_node.elem_type == 'int'
    def is_string(self, source_node):
        return source_node.elem_type == 'string'
    
    def get_variable_name(self, statement_node):
        if statement_node.elem_type == '=':
            return statement_node.dict['name']
        else:
            super().error(
                ErrorType.TYPE_ERROR,
                "Cannot access variable name of a function, use get_function_name instead",
            )
    def get_value(self, value_node):
        if self.is_int(value_node):
            return int(value_node.dict['val'])
        else:
            return value_node.dict['val']

    def get_expression(self, statement_node):
        return statement_node.dict['expression']
    
    # DESIGN NOTE -- EVALUATE EXPRESSION HERE OR IN ACTUAL DO_PRINT FUNCTION??
    def get_arguments_to_print(self, print_statement_node):
        arguments = print_statement_node.dict['args']

        evaluated_arguments = []

        for argument in arguments:
            evaluated_arguments.append(self.evaluate_expression(argument))
        
        return evaluated_arguments
    
    def evaluate_operation(self, operation_node):
        op1 = self.evaluate_expression(operation_node.dict['op1'])
        op2 = self.evaluate_expression(operation_node.dict['op2'])
        operation = operation_node.elem_type

        if isinstance(op1, str) or isinstance(op2, str):
            super().error(
                ErrorType.TYPE_ERROR,
                "Cannot add or subtract strings",
            )

        if type(op1) != type(op2):
            super().error(
                ErrorType.TYPE_ERROR,
                "Cannot add or subtract different types",
            )
        
        match operation:
            case '+':
                return op1 + op2
            case '-':
                return op1 - op2
            case _:
                super().error(
                    ErrorType.NAME_ERROR,
                    "Unknown operation",
                )

    def evaluate_expression(self, expression_node):
        if self.is_value(expression_node):
            return self.get_value(expression_node)
        if self.is_variable(expression_node):
            variable_name = expression_node.dict['name']
            if variable_name not in self.variable_name_to_value:
                super().error(
                    ErrorType.NAME_ERROR,
                    "Trying to access undeclared variable",
                )
                ## TODO -- DO I RETURN AFTER RAISING AN ERROR??
            else:
                return self.variable_name_to_value[variable_name]
        if self.is_operation(expression_node):
            return self.evaluate_operation(expression_node)
        # only valid function call in an expression is inputi
        if self.is_function(expression_node):
            if expression_node.dict['name'] == 'print':
                super().error(
                    ErrorType.TYPE_ERROR,
                    "Cannot call print inside of an expression",
                )
            else:
                return self.do_function(expression_node)
