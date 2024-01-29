firsts = {"Program": ["int", "void", "EPSILON"], "DeclarationList": ["int", "void", "EPSILON"], "Declaration": ["int", "void"], "DeclarationInitial": ["int", "void"], "DeclarationPrime": [";", "[", "("], "VarDeclarationPrime": [";", "["], "FunDeclarationPrime": ["("], "TypeSpecifier": ["int", "void"], "Params": ["int", "void"], "ParamList": [",", "EPSILON"], "Param": ["int", "void"], "ParamPrime": ["[", "EPSILON"], "CompoundStmt": ["{"], "StatementList": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-", "EPSILON"], "Statement": ["ID", ";", "NUM", "(", "{", "break", "if", "while", "return", "+", "-"], "ExpressionStmt": ["ID", ";", "NUM", "(", "break", "+", "-"], "SelectionStmt": ["if"], "IterationStmt": ["while"], "ReturnStmt": ["return"], "ReturnStmtPrime": ["ID", ";", "NUM", "(", "+", "-"], "Expression": ["ID", "NUM", "(", "+", "-"], "B": ["[", "(", "=", "<", "==", "+", "-", "*", "EPSILON"], "H": ["=", "<", "==", "+", "-", "*", "EPSILON"], "SimpleExpressionZegond": ["NUM", "(", "+", "-"], "SimpleExpressionPrime": ["(", "<", "==", "+", "-", "*", "EPSILON"], "C": ["<", "==", "EPSILON"], "Relop": ["<", "=="], "AdditiveExpression": ["ID", "NUM", "(", "+", "-"], "AdditiveExpressionPrime": ["(", "+", "-", "*", "EPSILON"], "AdditiveExpressionZegond": ["NUM", "(", "+", "-"], "D": ["+", "-", "EPSILON"], "Addop": ["+", "-"], "Term": ["ID", "NUM", "(", "+", "-"], "TermPrime": ["(", "*", "EPSILON"], "TermZegond": ["NUM", "(", "+", "-"], "G": ["*", "EPSILON"], "SignedFactor": ["ID", "NUM", "(", "+", "-"], "SignedFactorPrime": ["(", "EPSILON"], "SignedFactorZegond": ["NUM", "(", "+", "-"], "Factor": ["ID", "NUM", "("], "VarCallPrime": ["[", "(", "EPSILON"], "VarPrime": ["[", "EPSILON"], "FactorPrime": ["(", "EPSILON"], "FactorZegond": ["NUM", "("], "Args": ["ID", "NUM", "(", "+", "-", "EPSILON"], "ArgList": ["ID", "NUM", "(", "+", "-"], "ArgListPrime": [",", "EPSILON"]}
follows = {"Program": ["$"], "DeclarationList": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "while", "return", "+", "-", "$"], "Declaration": ["ID", ";", "NUM", "(", "int", "void", "{", "}", "break", "if", "while", "return", "+", "-", "$"], "DeclarationInitial": [";", "[", "(", ")", ","], "DeclarationPrime": ["ID", ";", "NUM", "(", "int", "void", "{", "}", "break", "if", "while", "return", "+", "-", "$"], "VarDeclarationPrime": ["ID", ";", "NUM", "(", "int", "void", "{", "}", "break", "if", "while", "return", "+", "-", "$"], "FunDeclarationPrime": ["ID", ";", "NUM", "(", "int", "void", "{", "}", "break", "if", "while", "return", "+", "-", "$"], "TypeSpecifier": ["ID"], "Params": [")"], "ParamList": [")"], "Param": [")", ","], "ParamPrime": [")", ","], "CompoundStmt": ["ID", ";", "NUM", "(", "int", "void", "{", "}", "break", "if", "else", "while", "return", "+", "-", "$"], "StatementList": ["}"], "Statement": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "ExpressionStmt": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "SelectionStmt": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "IterationStmt": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "ReturnStmt": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "ReturnStmtPrime": ["ID", ";", "NUM", "(", "{", "}", "break", "if", "else", "while", "return", "+", "-"], "Expression": [";", "]", ")", ","], "B": [";", "]", ")", ","], "H": [";", "]", ")", ","], "SimpleExpressionZegond": [";", "]", ")", ","], "SimpleExpressionPrime": [";", "]", ")", ","], "C": [";", "]", ")", ","], "Relop": ["ID", "NUM", "(", "+", "-"], "AdditiveExpression": [";", "]", ")", ","], "AdditiveExpressionPrime": [";", "]", ")", ",", "<", "=="], "AdditiveExpressionZegond": [";", "]", ")", ",", "<", "=="], "D": [";", "]", ")", ",", "<", "=="], "Addop": ["ID", "NUM", "(", "+", "-"], "Term": [";", "]", ")", ",", "<", "==", "+", "-"], "TermPrime": [";", "]", ")", ",", "<", "==", "+", "-"], "TermZegond": [";", "]", ")", ",", "<", "==", "+", "-"], "G": [";", "]", ")", ",", "<", "==", "+", "-"], "SignedFactor": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "SignedFactorPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "SignedFactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "Factor": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "VarCallPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "VarPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "FactorPrime": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "FactorZegond": [";", "]", ")", ",", "<", "==", "+", "-", "*"], "Args": [")"], "ArgList": [")"], "ArgListPrime": [")"]}
terminals = ['ID', ';', '[', 'NUM', ']', '(', ')', 'int', 'void', ',', '{', '}', 'break', 'if', 'else', 'while', 'return', '=', '<', '==', '+', '-', '*', '$']
rules = {"Program": [["DeclarationList"]], 
        "DeclarationList": [["Declaration", "DeclarationList"], []],
        "Declaration": [["DeclarationInitial", "DeclarationPrime"]],
        "DeclarationInitial": [["TypeSpecifier", "#pnext", "ID"]], 
        "DeclarationPrime": [["FunDeclarationPrime"], ["VarDeclarationPrime", "#pvar"]], 
        "VarDeclarationPrime": [[";"], ["[", "#pnext", "NUM", "]", ";"]],
        "FunDeclarationPrime": [["#func_start", "(", "Params", ")", "CompoundStmt", "#func_end"]],  # added actions until here
        "TypeSpecifier": [["#type", "int"], ["#type", "void"]], 
        "Params": [["int", "#pnext", "ID", "ParamPrime", "ParamList"], ["void"]], 
        "ParamList": [[",", "Param", "ParamList"], []], 
        "Param": [["DeclarationInitial", "ParamPrime"]], 
        "ParamPrime": [["[", "#parray", "]"], []], 
        "CompoundStmt": [["{", "DeclarationList", "StatementList", "}"]], 
        "StatementList": [["Statement", "StatementList"], []], 
        "Statement": [["ExpressionStmt"], ["CompoundStmt"], ["SelectionStmt"], ["IterationStmt"], ["ReturnStmt"]], 
        "ExpressionStmt": [["Expression", ";"], ["break", ";"], [";"]], 
        "SelectionStmt": [["if", "(", "Expression", ")", "Statement", "else", "Statement"]], 
        "IterationStmt": [["#scope_plus", "while", "(", "Expression", ")", "Statement", "#scope_minus"]], 
        "ReturnStmt": [["return", "ReturnStmtPrime"]], 
        "ReturnStmtPrime": [[";"], ["Expression", ";"]], 
        "Expression": [["SimpleExpressionZegond"], ["ID", "B"]], 
        "B": [["=", "Expression"], ["[", "Expression", "]", "H"], ["SimpleExpressionPrime"]], 
        "H": [["=", "Expression"], ["G", "D", "C"]], 
        "SimpleExpressionZegond": [["AdditiveExpressionZegond", "C"]], 
        "SimpleExpressionPrime": [["AdditiveExpressionPrime", "C"]], 
        "C": [["Relop", "AdditiveExpression"], []], 
        "Relop": [["<"], ["=="]], 
        "AdditiveExpression": [["Term", "D"]], 
        "AdditiveExpressionPrime": [["TermPrime", "D"]], 
        "AdditiveExpressionZegond": [["TermZegond", "D"]], 
        "D": [["Addop", "Term", "D"], []], 
        "Addop": [["+"], ["-"]], 
        "Term": [["SignedFactor", "G"]], 
        "TermPrime": [["SignedFactorPrime", "G"]],
        "TermZegond": [["SignedFactorZegond", "G"]], 
        "G": [["*", "SignedFactor", "G"], []], 
        "SignedFactor": [["+", "Factor"], ["-", "Factor"], ["Factor"]], 
        "SignedFactorPrime": [["FactorPrime"]], 
        "SignedFactorZegond": [["+", "Factor"], ["-", "Factor"], ["FactorZegond"]], 
        "Factor": [["(", "Expression", ")"], ["ID", "VarCallPrime"], ["NUM"]], 
        "VarCallPrime": [["(", "Args", ")"], ["VarPrime"]], 
        "VarPrime": [["[", "Expression", "]"], []], 
        "FactorPrime": [["(", "Args", ")"], []], 
        "FactorZegond": [["(", "Expression", ")"], ["NUM"]], 
        "Args": [["ArgList"], []], 
        "ArgList": [["Expression", "ArgListPrime"]], 
        "ArgListPrime": [[",", "Expression", "ArgListPrime"], []]
}