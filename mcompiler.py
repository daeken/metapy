import pprint, tokenizer
from macro import *
import compiler.ast as ast
from compiler.misc import set_filename
from compiler.pycodegen import ModuleCodeGenerator

class Compiler(object):
	class AssMacro(OperMacro):
	  syntax = Var(str), '=', Var
	  def handle(self, left, right):
	    return ast.Assign(
	    	[ast.AssName(left, 'OP_ASSIGN')], 
	    	right
	    )
	
	class CommaMacro(OperMacro):
		syntax = Var, ',', Var
		def handle(self, left, right):
			print left, right
			if not isinstance(left, list):
				left = [left]
			if not isinstance(right, list):
				right = [right]
			return left + right
	
	class DefMacro(Macro):
		syntax = 'def', Var(str), Var, Var
		def handle(self, name, args, body):
			return ast.Function(
					None,           # Decorators
					name,           # Name
					[],             # Argnames
					[],             # Defaults
					0,              # Flags
					None,           # Doc
					ast.Stmt(body)  # Code
				)
	
	class DotMacro(OperMacro):
		syntax = Var, '.', Var
		def handle(self, left, right):
			return ast.Getattr(left, right)
	
	class PrintMacro(Macro):
		syntax = 'print', Var
		def handle(self, stmt):
			return ast.Printnl([stmt], None)
	
	# Flow control
	class IfMacro(Macro):
		syntax = 'if', Var, Var
		def handle(self, cond, body):
			return ast.If([(cond, ast.Stmt(body))], None)
	class WhileMacro(Macro):
		syntax = 'while', Var, Var
		def handle(self, cond, body):
			return ast.While(cond, ast.Stmt(body), None)
	
	# Comparisons
	class EqMacro(OperMacro):
		syntax = Var, '==', Var
		def handle(self, left, right):
			return ast.Compare(left, [('==', right)])
	class LtMacro(OperMacro):
		syntax = Var, '<', Var
		def handle(self, left, right):
			return ast.Compare(left, [('<', right)])
	class GtMacro(OperMacro):
		syntax = Var, '>', Var
		def handle(self, left, right):
			return ast.Compare(left, [('>', right)])
	class LeMacro(OperMacro):
		syntax = Var, '<=', Var
		def handle(self, left, right):
			return ast.Compare(left, [('<=', right)])
	class GeMacro(OperMacro):
		syntax = Var, '>=', Var
		def handle(self, left, right):
			return ast.Compare(left, [('>=', right)])
	
	# Arithmetic
	class IncMacro(OperMacro):
		syntax = Var, '++'
		def handle(self, var):
			return ast.AugAssign(var, '+=', ast.Const(1))
	class DecMacro(OperMacro):
		syntax = Var, '--'
		def handle(self, var):
			return ast.AugAssign(var, '-=', ast.Const(1))
	class AddMacro(OperMacro):
		syntax = Var, '+', Var
		def handle(self, left, right):
			return ast.Add(left, right)
	class SubMacro(OperMacro):
		syntax = Var, '-', Var
		def handle(self, left, right):
			return ast.Sub(left, right)
	class MulMacro(OperMacro):
		syntax = Var, '*', Var
		def handle(self, left, right):
			return ast.Mul(left, right)
	class DivMacro(OperMacro):
		syntax = Var, '/', Var
		def handle(self, left, right):
			return ast.Div(left, right)
	class ModMacro(OperMacro):
		syntax = Var, '%', Var
		def handle(self, left, right):
			return ast.Mod(left, right)
	class PowMacro(OperMacro):
		syntax = Var, '**', Var
		def handle(self, left, right):
			return ast.Power(left, right)
	class BAndMacro(OperMacro):
		syntax = Var, '&', Var
		def handle(self, left, right):
			return ast.Bitand(left, right)
	class BOrMacro(OperMacro):
		syntax = Var, '|', Var
		def handle(self, left, right):
			return ast.Bitor(left, right)
	class BXorMacro(OperMacro):
		syntax = Var, '^', Var
		def handle(self, left, right):
			return ast.Bitxor(left, right)
	
	# Boolean
	class AndMacro(OperMacro):
		syntax = Var, 'and', Var
		def handle(self, left, right):
			return ast.And([left, right])
	class SAndMacro(OperMacro):
		syntax = Var, '&&', Var
		def handle(self, left, right):
			return ast.And([left, right])
	class OrMacro(OperMacro):
		syntax = Var, 'or', Var
		def handle(self, left, right):
			return ast.Or([left, right])
	class SOrMacro(OperMacro):
		syntax = Var, '||', Var
		def handle(self, left, right):
			return ast.Or([left, right])
	
	def __init__(self, source):
		self.macros = []
		for mem in dir(self):
			mem = getattr(self, mem)
			if isinstance(mem, type) and issubclass(mem, Macro):
				self.macros.append(mem(self))
		
		tokens = tokenizer.tokenize(source)
		pprint.pprint(tokens)
		
		code = self.compile(tokens)
		pprint.pprint(code)
		
		code = ast.Module(
				None,
				ast.Stmt(code)
			)
		
		print code
		set_filename('<macropy>', code)
		self.compiled = ModuleCodeGenerator(code).getCode()
	
	def compile(self, alist, ctype=None):
		if isinstance(alist, ast.Node):
			return alist
		elif isinstance(alist, tokenizer.Number):
			if ctype == int:
				return int(eval(alist))
			elif ctype == long:
				return long(eval(alist))
			elif ctype == float:
				return float(eval(alist))
			else:
				return ast.Const(eval(alist))
		elif isinstance(alist, str):
			if alist[0] in '\'"':
				return ast.Const(eval(alist))
			else:
				if ctype == str:
					return alist
				else:
					return ast.Name(alist)
		
		i = 0
		while i < len(alist):
			elem = alist[i]
			if isinstance(elem, list):
				for macro in self.macros:
					rep = macro.match(elem)
					if rep != None:
						alist[i] = rep
						i -= 1
						break
			i += 1
		return alist
