        
def spinnerWork(spinner, thread, worker, func):
    """
    Starts a spinner and moves a worker to a separate thread.

    Args:
        spinner: The spinner object to display.
        thread: The thread to move the worker to.
        worker: The worker object to move to the thread.
        func: The function to connect to the worker's result signal.

    Returns:
        None
    """
    try:
        spinner.show()
        spinner.start()

        worker.moveToThread(thread)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.result.connect(func)
        thread.started.connect(worker.run)
        thread.finished.connect(spinner.stop)

        thread.start()
    except Exception as e:
         return
    