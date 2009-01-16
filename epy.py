from compiler.ast import *
from pprint import pprint

from macro import *
from py25 import Py25

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
	
	# Flow control
	class SwitchMacro(Macro):
		syntax = 'switch', Var, Var
		def handle(self, val, body):
			if isinstance(val, Name):
				var = val
			else:
				var = Name(self.compiler.makeTempVar())
			
			cases = []
			default = None
			for case in body:
				if case[0].name == 'case':
					_, dval, body = case
					body = Stmt(self.compiler.compile(body))
					cases.append((Compare(var, [('==', dval)]), body))
				elif case[0].name == 'default':
					if len(case) == 3:
						_, dvar, body = case
						self.compiler.walkReplace(body, dvar.name, var)
						default = Stmt(self.compiler.compile(body))
					else:
						default = Stmt(self.compiler.compile(case[1]))
				else:
					print 'Parse error'
			
			match = If(
					cases,
					default
				)
			if isinstance(val, Name):
				return match
			else:
				return Stmt(
						[
							Assign(
								[AssName(var.name, 'OP_ASSIGN')], 
								val
							), 
							match,
							AssName(var.name, 'OP_DELETE')
						]
					)
	
	# Boolean
	class SAndMacro(OperMacro):
		syntax = Var, '&&', Var
		precedence = 210
		def handle(self, left, right):
			return And([left, right])
	class SOrMacro(OperMacro):
		syntax = Var, '||', Var
		precedence = 220
		def handle(self, left, right):
			return Or([left, right])
	
	# Misc
	class IsaMacro(OperMacro):
		syntax = Var, 'isa', Var
		def handle(self, var, type):
			return ast.CallFunc(ast.Name('isinstance'), [var, type], None, None)
