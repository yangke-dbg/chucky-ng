
from joern_nodes import Function

"""
Selection of functions based on different criteria,
e.g., symbol usage
"""

class FunctionSelector:

    # FIXME: introduce functions that only retrieve symbol
    # nodes and not entire nodes as that will greatly
    # improve performance

    """
    Determine functions using the same symbol as the
    function of interest
    """
    def selectFunctionsUsingSymbol(self, symbol):
        if symbol.target_type == 'Parameter':
            functions = Function.lookup_functions_by_parameter(
                    symbol.target_name,
                    symbol.target_decl_type)
        elif symbol.target_type == 'Variable':
            functions = Function.lookup_functions_by_variable(
                    symbol.target_name,
                    symbol.target_decl_type)
        elif symbol.target_type == 'Callee':
            functions = Function.lookup_functions_by_callee(
                    symbol.target_name)
        
        return functions