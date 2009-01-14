from macro import *
from py25 import Py25
from compiler.ast import *

class EPy(Py25):
	# Arithmetic
	class IncMacro(OperMacro):
		syntax = Var, '++'
		def handle(self, var):
			return ast.AugAssign(var, '+=', ast.Const(1))
	class DecMacro(OperMacro):
		syntax = Var, '--'
		def handle(self, var):
			return ast.AugAssign(var, '-=', ast.Const(1))
	
	# Misc
	class IsaMacro(OperMacro):
		syntax = Var, 'isa', Var
		def handle(self, var, type):
			return ast.CallFunc(ast.Name('isinstance'), [var, type], None, None)
