from twisted.internet import threads

def work_then_callback(work, callback, work_args=None):
    """
    Runs `work` asynchronously, and then passes the result to
    `callback_function`.
    """
    if work_args is None:
        work_args = []
    threads.deferToThread(work, *work_args).addCallback(callback)
