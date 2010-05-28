from twisted.internet import threads

def work_then_callback(work_function, callback_function, work_args=[]):
	"""
	Runs `work_function` asynchronously, and then passes the result to
	`callback_function`.
	"""
	threads.deferToThread(
		work_function,
		*work_args
	).addCallback(callback_function)
