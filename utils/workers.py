        
def spinnerWork(spinner, thread, worker, func):
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
    