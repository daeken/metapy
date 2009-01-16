import re

nameRE = re.compile('^([a-zA-Z_][a-zA-Z0-9_]*)')
numberRE = re.compile('^(-?[0-9]+[lLfFdD]?|-?[0-9]+\.[0-9]*[fFdD]?|0x[0-9a-fA-F]+[lL]?)')
opRE = re.compile('^([+\-*/<>=!@#$%^&?.,:;]+)')
matchingGroup = {
		')' : '(',
		'}' : '{',
		']' : '[',
		'`' : '`'
	}

class Op(str):
	def __repr__(self):
		return 'OP' + self

class Number(str):
	def __repr__(self):
		return '#' + str(self)

def tokenize(source):
	toke = Tokenizer(source)
	return toke.ret

class Tokenizer(object):
	def __init__(self, source):
		push, pop = self.push, self.pop
		source = [line.rstrip() for line in source if line.strip()]
		
		self.ret = []
		self.stack = [self.ret]
		self.closures = [self.stack]
		self.top = self.ret
		level = 0
		self.groups = 0
		passBlock = None
		
		for line in source:
			end = len(line)
			line = line.lstrip()
			# XXX: Handle spaces
			pos = end - len(line)
			
			if self.groups == 0:
				if pos > level and passBlock != None:
					new = []
					self.stack = [new]
					self.closures.append(self.stack)
					self.top = new
					passBlock.append(new)
					passBlock = None
				elif pos < level:
					self.closures = self.closures[:pos-level]
					self.stack = self.closures[-1][:-1]
					self.top = self.stack[-1]
				level = pos
			
			if self.groups == 0:
				push()
			while pos < end:
				tsize = None
				if self.isEnd(line):
					if line == ':':
						passBlock = self.top
					tsize = 1
				elif line[0] in '\'"':
					escape = False
					for i in xrange(1, len(line)):
						if escape:
							escape = False
							continue
						if line[i] == line[0]:
							break
						elif line[i] == '\\':
							escape = True
					self.top.append(line[:i+1])
					tsize = i+1
				elif line[0] in '({[`' and (line[0] != '`' or self.top[0] != '`'):
					push()
					self.top.append(line[0])
					tsize = 1
					self.groups += 1
				elif line[0] in ')}]`':
					assert self.top[0] == matchingGroup[line[0]]
					self.top.append(line[0])
					pop()
					tsize = 1
					self.groups -= 1
				else:
					match = opRE.match(line)
					if match:
						name = match.groups()[0]
						self.top.append(Op(name))
						tsize = len(name)
					else:
						match = nameRE.match(line)
						if match:
							name = match.groups()[0]
							self.top.append(name)
							tsize = len(name)
						else:
							match = numberRE.match(line)
							if match:
								name = match.groups()[0]
								self.top.append(Number(name))
								tsize = len(name)
							else:
								print 'Parse error', line
								break
				
				if tsize:
					line = line[tsize:].lstrip()
					pos = end - len(line)
			if self.groups == 0:
				pop()
	def push(self):
		new = []
		self.top.append(new)
		self.stack.append(new)
		self.top = new
	def pop(self):
		self.stack = self.stack[:-1]
		self.top = self.stack[-1]
	def isEnd(self, line):
		if line[0] != ':':
			return False
		elif line == ':':
			return True
		
		if self.groups:
			return False
		
		if line[1] in ' \t':
			return True
		
		if opRE.match(line[1:]):
			return False
		return True
