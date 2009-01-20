from compiler.ast import *

class Var(object):
	def __init__(self, type=None):
		self.type = type

class Optional(list):
	def __init__(self, *args):
		list.__init__(self, args)

class ZeroOrMore(list):
	def __init__(self, *args):
		list.__init__(self, args)

class OneOrMore(list):
	def __init__(self, *args):
		list.__init__(self, args)

class Macro(object):
	syntax = None
	subCompile = True
	precedence = 0
	def __init__(self, compiler):
		if not isinstance(self.syntax, list) and not isinstance(self.syntax, tuple):
			self.syntax = (self.syntax, )
		self.compiler = compiler
		self.alist = None
		self.pos = None
	def match(self, alist, syntax=None, partial=False):
		if syntax == None:
			doCall = True
			syntax = self.syntax
		else:
			doCall = False
		
		if not isinstance(alist, list) and not isinstance(alist, tuple):
			return None
		
		if self.alist != None:
			save = self.alist, self.apos
		else:
			save = None, None
		
		self.alist = [isinstance(elem, Name) and elem.name or elem for elem in alist]
		self.apos = 0
		
		args = self.recmatch(syntax, [])
		if args == None or (not partial and self.apos != len(self.alist)):
			self.alist, self.apos = save
			return None
		
		apos = self.apos
		
		if doCall:
			args = self.handle(*args)
		
		self.alist, self.apos = save
		
		if partial and args != None:
			return apos, args
		else:
			return args
	
	def recmatch(self, syntax, args):
		synpos = 0
		while self.apos < len(self.alist) and synpos < len(syntax):
			oelem = self.alist[self.apos]
			syn = syntax[synpos]
			if isinstance(syn, ZeroOrMore) or isinstance(syn, OneOrMore):
				if synpos >= len(args):
					args.append([])
				if len(syn) > 1:
					ret = self.recmatch(syn, [])
					if ret == None:
						if isinstance(syn, OneOrMore) and len(args[-1]) == 0:
							return None
						synpos += 1
					else:
						if len(ret) == 1:
							ret = ret[0]
						args[-1].append(ret)
					continue
				
				rep = self.submatch(oelem, syn[0])
				if rep == None:
					if isinstance(syn, OneOrMore) and len(args[-1]) == 0:
						return None
					else:
						synpos += 1
				else:
					if rep != True:
						args.append(rep)
					synpos += 1
					self.apos += 1
			elif isinstance(syn, Optional):
				if len(syn) > 1:
					ret = self.recmatch(syn, [])
					if ret == None:
						args.append(None)
						synpos += 1
					else:
						if len(ret) == 1:
							ret = ret[0]
						args.append(ret)
						synpos += 1
					continue
				
				rep = self.submatch(oelem, syn[0])
				args.append(rep)
				synpos += 1
				if rep != None:
					self.apos += 1
			else:
				rep = self.submatch(oelem, syn)
				if rep == None:
					return None
				else:
					if rep != True:
						args.append(rep)
					synpos += 1
					self.apos += 1
		
		if synpos < len(syntax):
			return None
		
		return args
	
	def submatch(self, oelem, elem):
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
			return celem
		elif isinstance(elem, str):
			if elem != oelem:
				return None
			return True
	
	def __cmp__(self, b):
		if isinstance(self, OperMacro) and not isinstance(b, OperMacro):
			return 1
		elif not isinstance(self, OperMacro) and isinstance(b, OperMacro):
			return -1
		
		return cmp(self.precedence, b.precedence)

class MLMacro(Macro):
	def match(self, alist):
		args = []
		apos = 0
		synpos = 0
		while apos < len(alist):
			if synpos >= len(args) and (
					isinstance(self.syntax[synpos], ZeroOrMore) or 
					isinstance(self.syntax[synpos], OneOrMore)
				):
				args.append([])
			
			next = False
			rep = Macro.match(self, alist[apos], self.syntax[synpos])
			if rep == None:
				if isinstance(self.syntax[synpos], ZeroOrMore):
					next = True
				elif isinstance(self.syntax[synpos], OneOrMore):
					if len(args[-1]) > 0:
						next = True
					else:
						return None
				elif isinstance(self.syntax[synpos], Optional):
					args.append(None)
					next = True
				else:
					return None
			else:
				apos += 1
				if (
					isinstance(self.syntax[synpos], ZeroOrMore) or 
					isinstance(self.syntax[synpos], OneOrMore)
					):
					args[-1].append(rep)
				else:
					args.append(rep)
					next = True
			
			if next:
				synpos += 1
				if synpos == len(self.syntax):
					break
		
		for syn in self.syntax[synpos:]:
			if isinstance(syn, ZeroOrMore):
				args.append([])
			elif isinstance(syn, Optional):
				args.append(None)
			else:
				return None
		
		return apos, self.handle(*args)

class OperMacro(Macro):
	def match(self, alist):
		for start in xrange(len(alist)-1):
			rep = Macro.match(self, alist[start:], partial=True)
			if rep != None:
				used, rep = rep
				if not isinstance(rep, list):
					rep = [rep]
				ret = alist[:start] + rep + alist[start+used:]
				return ret
		return None
