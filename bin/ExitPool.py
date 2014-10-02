import multiprocessing.pool
from multiprocessing.util import debug

def worker(inqueue, outqueue, initializer=None, initargs=(), terminator=None, maxtasks=None):
	multiprocessing.pool.worker(inqueue, outqueue, initializer, initargs, maxtasks)
	if terminator is not None:
		terminator()


class ExitPool(multiprocessing.pool.Pool):

	def __init__(self, processes=None, initializer=None, initargs=(), terminator=None, maxtasksperchild=None):
		self._terminator = terminator
		if terminator is not None and not hasattr(terminator, '__call__'):
			raise TypeError('terminator must be callable')
		
		super(ExitPool,self).__init__(processes, initializer, initargs, maxtasksperchild)
		
		
		
	def _repopulate_pool(self):
		for i in range(self._processes - len(self._pool)):
			w = self.Process(target=worker, args=(self._inqueue, self._outqueue, self._initializer, 
				self._initargs, self._terminator, self._maxtasksperchild))
			self._pool.append(w)
			w.name = w.name.replace('Process', 'PoolWorker')
			w.daemon = True
			w.start()
			debug('added worker')
		