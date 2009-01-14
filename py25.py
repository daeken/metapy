from compiler.ast import *

from macro import *
from mcompiler import Compiler

class Py25(Compiler):
	class AssMacro(OperMacro):
	  syntax = Var(str), '=', Var
	  def handle(self, left, right):
	    return Assign(
	    	[AssName(left, 'OP_ASSIGN')], 
	    	right
	    )
	
	class CommaMacro(OperMacro):
		syntax = Var, ',', Var
		subCompile = False
		def handle(self, left, right):
			if not isinstance(left, list) and not isinstance(right, list):
				return [[left, right]]
			if not isinstance(left, list):
				left = [left]
			if not isinstance(right, list):
				right = [right]
			return left + right
	
	class DefMacro(Macro):
		syntax = 'def', Var(str), Var, Var
		def handle(self, name, args, body):
			return Function(
					None,           # Decorators
					name,           # Name
					[],             # Argnames
					[],             # Defaults
					0,              # Flags
					None,           # Doc
					Stmt(body)  # Code
				)
	
	class DotMacro(OperMacro):
		syntax = Var, '.', Var
		def handle(self, left, right):
			return Getattr(left, right)
	
	class PrintMacro(Macro):
		syntax = 'print', Var
		def handle(self, stmt):
			return Printnl([stmt], None)
	
	class CallMacro(OperMacro):
		syntax = Var(Node), Var(list)
		def handle(self, target, args):
			if args[0] != '(':
				return None
			args = self.compiler.compile(args)
			return CallFunc(target, args, None, None)
	
	# Flow control
	class ForMacro(Macro):
		syntax = 'for', Var(str), 'in', Var, Var
		def handle(self, var, iter, body):
			return For(AssName(var, 'OP_ASSIGN'), iter, Stmt(body), None)
	class ForTupleMacro(Macro):
		syntax = 'for', Var(list), 'in', Var, Var
		def handle(self, vars, iter, body):
			return For(
				AssTuple([AssName(hasattr(var, 'name') and var.name or var, 'OP_ASSIGN') for var in vars]), 
				iter, 
				Stmt(body), 
				None
			)
	class IfMacro(Macro):
		syntax = 'if', Var, Var
		def handle(self, cond, body):
			return If([(cond, Stmt(body))], None)
	class WhileMacro(Macro):
		syntax = 'while', Var, Var
		def handle(self, cond, body):
			return While(cond, Stmt(body), None)
	
	# Comparisons
	class EqMacro(OperMacro):
		syntax = Var, '==', Var
		def handle(self, left, right):
			return Compare(left, [('==', right)])
	class LtMacro(OperMacro):
		syntax = Var, '<', Var
		def handle(self, left, right):
			return Compare(left, [('<', right)])
	class GtMacro(OperMacro):
		syntax = Var, '>', Var
		def handle(self, left, right):
			return Compare(left, [('>', right)])
	class LeMacro(OperMacro):
		syntax = Var, '<=', Var
		def handle(self, left, right):
			return Compare(left, [('<=', right)])
	class GeMacro(OperMacro):
		syntax = Var, '>=', Var
		def handle(self, left, right):
			return Compare(left, [('>=', right)])
	
	# Arithmetic
	class AddMacro(OperMacro):
		syntax = Var, '+', Var
		def handle(self, left, right):
			return Add(left, right)
	class AssAddMacro(OperMacro):
		syntax = Var, '+=', Var
		def handle(self, left, right):
			return AugAssign(left, '+=', right)
	class SubMacro(OperMacro):
		syntax = Var, '-', Var
		def handle(self, left, right):
			return Sub(left, right)
	class AssSubMacro(OperMacro):
		syntax = Var, '-=', Var
		def handle(self, left, right):
			return AugAssign(left, '-=', right)
	class MulMacro(OperMacro):
		syntax = Var, '*', Var
		def handle(self, left, right):
			return Mul(left, right)
	class AssMulMacro(OperMacro):
		syntax = Var, '*=', Var
		def handle(self, left, right):
			return AugAssign(left, '*=', right)
	class DivMacro(OperMacro):
		syntax = Var, '/', Var
		def handle(self, left, right):
			return Div(left, right)
	class AssDivMacro(OperMacro):
		syntax = Var, '/=', Var
		def handle(self, left, right):
			return AugAssign(left, '/=', right)
	class ModMacro(OperMacro):
		syntax = Var, '%', Var
		def handle(self, left, right):
			return Mod(left, right)
	class AssModMacro(OperMacro):
		syntax = Var, '%=', Var
		def handle(self, left, right):
			return AugAssign(left, '%=', right)
	class PowMacro(OperMacro):
		syntax = Var, '**', Var
		def handle(self, left, right):
			return Power(left, right)
	class AssPowMacro(OperMacro):
		syntax = Var, '**=', Var
		def handle(self, left, right):
			return AugAssign(left, '**=', right)
	class BAndMacro(OperMacro):
		syntax = Var, '&', Var
		def handle(self, left, right):
			return Bitand(left, right)
	class AssBAndMacro(OperMacro):
		syntax = Var, '&=', Var
		def handle(self, left, right):
			return AugAssign(left, '&=', right)
	class BOrMacro(OperMacro):
		syntax = Var, '|', Var
		def handle(self, left, right):
			return Bitor(left, right)
	class AssBOrMacro(OperMacro):
		syntax = Var, '|=', Var
		def handle(self, left, right):
			return AugAssign(left, '|=', right)
	class BXorMacro(OperMacro):
		syntax = Var, '^', Var
		def handle(self, left, right):
			return Bitxor(left, right)
	class AssBXorMacro(OperMacro):
		syntax = Var, '^=', Var
		def handle(self, left, right):
			return AugAssign(left, '^=', right)
	
	# Boolean
	class AndMacro(OperMacro):
		syntax = Var, 'and', Var
		def handle(self, left, right):
			return And([left, right])
	class SAndMacro(OperMacro):
		syntax = Var, '&&', Var
		def handle(self, left, right):
			return And([left, right])
	class OrMacro(OperMacro):
		syntax = Var, 'or', Var
		def handle(self, left, right):
			return Or([left, right])
	class SOrMacro(OperMacro):
		syntax = Var, '||', Var
		def handle(self, left, right):
			return Or([left, right])
