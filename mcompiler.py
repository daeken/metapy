import pprint, tokenizer
from compiler.ast import *
from compiler.misc import set_filename
from compiler.pycodegen import ModuleCodeGenerator

from macro import Macro

class Compiler(object):
	def __init__(self, source):
		self.macros = []
		for mem in dir(self):
			mem = getattr(self, mem)
			if isinstance(mem, type) and issubclass(mem, Macro):
				self.macros.append(mem(self))
		self.macros.sort()
		
		tokens = tokenizer.tokenize(source)
		pprint.pprint(tokens)
		
		code = self.compile(tokens)
		pprint.pprint(code)
		
		code = Module(
				None,
				Stmt(code)
			)
		
		print code
		set_filename('<macropy>', code)
		self.compiled = ModuleCodeGenerator(code).getCode()
	
	def compileElem(self, elem, ctype=None):
		if isinstance(elem, Node):
			return elem
		elif isinstance(elem, tokenizer.Number):
			if ctype in (int, long, float):
				return ctype(eval(elem))
			else:
				return Const(eval(elem))
		elif isinstance(elem, str):
			if elem[0] in '\'"':
				return Const(eval(elem))
			elif ctype == str or isinstance(elem, tokenizer.Op):
				return elem
			else:
				return Name(str(elem))
		else:
			return elem
	
	def compile(self, alist, ctype=None, keepList=False):
		if isinstance(alist, list):
			if ctype == list:
				return alist
		else:
			return self.compileElem(alist, ctype)
		
		if len(alist) and not isinstance(alist[0], list):
			if alist[0] == '(':
				rep = self.compile([alist[1:-1]], ctype)
				if not keepList and isinstance(rep, list) and len(rep) == 1:
					return rep[0]
				return rep
		
		change = True
		while change:
			change = False
			i = 0
			for i in xrange(len(alist)):
				elem = alist[i]
				if isinstance(elem, list):
					for macro in self.macros:
						rep = macro.match(elem)
						if rep != None:
							change = True
							alist[i] = rep
							i -= 1
							break
					else:
						for j in xrange(len(elem)):
							elem[j] = self.compileElem(elem[j])
				else:
					alist[i] = self.compileElem(elem)
				i += 1
		return alist
