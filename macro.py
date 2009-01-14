import compiler.ast as ast

class Var(object):
	def __init__(self, type=None):
		self.type = type

class Macro(object):
	syntax = None
	subCompile = True
	def __init__(self, compiler):
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
			celem = alist[i]
			if elem == Var or isinstance(elem, Var):
				if self.subCompile:
					args.append(self.compiler.compile(celem, isinstance(elem, Var) and elem.type or None))
				else:
					args.append(celem)
			elif isinstance(elem, str):
				if elem != celem:
					return None
		
		return self.handle(*args)

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
