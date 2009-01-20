from compiler.ast import *

from macro import *
from mcompiler import Compiler

class Py25(Compiler):
	class AssMacro(OperMacro):
		syntax = Var, '=', Var
		precedence = 250
		def handle(self, left, right):
			if isinstance(left, Getattr):
				ass = AssAttr(left.expr, left.attrname, 'OP_ASSIGN')
			elif isinstance(left, Name):
				ass = AssName(left.name, 'OP_ASSIGN')
			else:
				raise Exception('Parse error', left)
			return Assign([ass], right)
	
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
	
	class ClassMacro(Macro):
		syntax = 'class', Var(str), Var
		def handle(self, name, body):
			return Class(
					name,
					[],
					None,
					Stmt(body)
				)
	
	class DefMacro(Macro):
		syntax = 'def', Var(str), Var, Var
		def handle(self, name, args, body):
			argnames = []
			for arg in args:
				if isinstance(arg, Name):
					argnames.append(arg.name)
				else:
					raise Exception('Parse error', args)
			return Function(
					None,           # Decorators
					name,           # Name
					argnames,       # Argnames
					[],             # Defaults
					0,              # Flags
					None,           # Doc
					Stmt(body)  # Code
				)
	
	class DotMacro(OperMacro):
		syntax = Var, '.', Var(str)
		precedence = 40
		def handle(self, left, right):
			return Getattr(left, right)
	
	class PrintMacro(Macro):
		syntax = 'print', Var
		def handle(self, stmts):
			if not isinstance(stmts, list):
				stmts = [stmts]
			return Printnl(stmts, None)
	
	class CallMacro(OperMacro):
		syntax = Var(Node), Var(list)
		precedence = 50
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
	class IfMacro(MLMacro):
		syntax = (
				('if', Var, Var),
				ZeroOrMore('elif', Var, Var),
				Optional('else', Var)
			)
		def handle(self, if_, elifs, else_):
			return If(
					[
						(cond, Stmt(body))
						for (cond, body) in [if_] + elifs
					],
					else_ != None and Stmt(else_) or None
				)
	class WhileMacro(Macro):
		syntax = 'while', Var, Var
		def handle(self, cond, body):
			return While(cond, Stmt(body), None)
	
	# Comparisons
	class EqMacro(OperMacro):
		syntax = Var, '==', Var
		precedence = 170
		def handle(self, left, right):
			return Compare(left, [('==', right)])
	class LtMacro(OperMacro):
		syntax = Var, '<', Var
		precedence = 170
		def handle(self, left, right):
			return Compare(left, [('<', right)])
	class GtMacro(OperMacro):
		syntax = Var, '>', Var
		precedence = 170
		def handle(self, left, right):
			return Compare(left, [('>', right)])
	class LeMacro(OperMacro):
		syntax = Var, '<=', Var
		precedence = 170
		def handle(self, left, right):
			return Compare(left, [('<=', right)])
	class GeMacro(OperMacro):
		syntax = Var, '>=', Var
		precedence = 170
		def handle(self, left, right):
			return Compare(left, [('>=', right)])
	
	# Arithmetic
	class AddMacro(OperMacro):
		syntax = Var, '+', Var
		precedence = 120
		def handle(self, left, right):
			return Add((left, right))
	class AssAddMacro(OperMacro):
		syntax = Var, '+=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '+=', right)
	class SubMacro(OperMacro):
		syntax = Var, '-', Var
		precedence = 121
		def handle(self, left, right):
			return Sub((left, right))
	class AssSubMacro(OperMacro):
		syntax = Var, '-=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '-=', right)
	class MulMacro(OperMacro):
		syntax = Var, '*', Var
		precedence = 110
		def handle(self, left, right):
			return Mul((left, right))
	class AssMulMacro(OperMacro):
		syntax = Var, '*=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '*=', right)
	class DivMacro(OperMacro):
		syntax = Var, '/', Var
		precedence = 111
		def handle(self, left, right):
			return Div((left, right))
	class AssDivMacro(OperMacro):
		syntax = Var, '/=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '/=', right)
	class ModMacro(OperMacro):
		syntax = Var, '%', Var
		precedence = 112
		def handle(self, left, right):
			return Mod((left, right))
	class AssModMacro(OperMacro):
		syntax = Var, '%=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '%=', right)
	class PowMacro(OperMacro):
		syntax = Var, '**', Var
		precedence = 80
		def handle(self, left, right):
			return Power((left, right))
	class AssPowMacro(OperMacro):
		syntax = Var, '**=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '**=', right)
	class BAndMacro(OperMacro):
		syntax = Var, '&', Var
		precedence = 140
		def handle(self, left, right):
			return Bitand((left, right))
	class AssBAndMacro(OperMacro):
		syntax = Var, '&=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '&=', right)
	class BOrMacro(OperMacro):
		syntax = Var, '|', Var
		precedence = 160
		def handle(self, left, right):
			return Bitor((left, right))
	class AssBOrMacro(OperMacro):
		syntax = Var, '|=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '|=', right)
	class BXorMacro(OperMacro):
		syntax = Var, '^', Var
		precedence = 150
		def handle(self, left, right):
			return Bitxor((left, right))
	class AssBXorMacro(OperMacro):
		syntax = Var, '^=', Var
		precedence = 250
		def handle(self, left, right):
			return AugAssign(left, '^=', right)
	
	# Boolean
	class AndMacro(OperMacro):
		syntax = Var, 'and', Var
		precedence = 210
		def handle(self, left, right):
			return And((left, right))
	class OrMacro(OperMacro):
		syntax = Var, 'or', Var
		precedence = 220
		def handle(self, left, right):
			return Or((left, right))
