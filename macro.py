import compiler.ast as ast

class Var(object):
	def __init__(self, type=None):
		self.type = type

class Macro(object):
	syntax = None
	subCompile = True
	precedence = 0
	def __init__(self, compiler):
		if not isinstance(self.syntax, list) and not isinstance(self.syntax, tuple):
			self.syntax = (self.syntax, )
		self.syntaxLen = len(self.syntax)
		self.compiler = compiler
	def match(self, alist):
		if isinstance(alist, ast.Node):
			return None
		elif len(alist) != self.syntaxLen:
			return None
		
		args = []
		for i in xrange(self.syntaxLen):
			elem = self.syntax[i]
			oelem = alist[i]
			if elem == Var or isinstance(elem, Var):
				if self.subCompile:
					celem = self.compiler.compile(oelem, isinstance(elem, Var) and elem.type or None)
				else:
					celem = oelem
				if (
					isinstance(elem, Var) and 
					not isinstance(celem, elem.type) and 
					not isinstance(oelem, elem.type)
				):
					return None
				args.append(celem)
			elif isinstance(elem, str):
				if elem != oelem:
					return None
		
		return self.handle(*args)
	
	def __cmp__(self, b):
		if isinstance(self, OperMacro) and not isinstance(b, OperMacro):
			return 1
		elif not isinstance(self, OperMacro) and isinstance(b, OperMacro):
			return -1
		
		return cmp(self.precedence, b.precedence)

class OperMacro(Macro):
	def match(self, alist):
		if len(alist) < self.syntaxLen:
			return None
		
		rep = Macro.match(self, alist)
		if rep != None:
			return rep
		
		for start in xrange(1, len(alist) - self.syntaxLen + 1):
			rep = Macro.match(self, alist[start:start+self.syntaxLen])
			if rep != None:
				if not isinstance(rep, list):
					rep = [rep]
				return alist[:start] + rep + alist[start+self.syntaxLen:]
		return None
