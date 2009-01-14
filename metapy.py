import sys, imp, marshal, struct, time

from epy import EPy

def main(fn):
	source = file(fn).readlines()
	compiler = EPy(source)
	pyc = file(fn.rsplit('.', 1)[0] + '2.pyc', 'wb')
	pyc.write(imp.get_magic())
	pyc.write(struct.pack('<l', time.time()))
	marshal.dump(compiler.compiled, pyc)
	pyc.close()

if __name__=='__main__':
	main(*sys.argv[1:])
