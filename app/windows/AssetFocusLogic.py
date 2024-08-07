import aiohttp

async def fetch(target, params, headers, logger):
        logger.log('info' ,f"Requesting URL: {target} with params: {params} and headers: {headers}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(target, params=params, headers=headers) as response:
                    response.raise_for_status()
                    financials = await response.json()
                    logger.log('info', 'Request Successful')
                    return financials
        except aiohttp.ClientError as e:
            logger.log('info', f"An error occurred while fetching data with params <{params}>", e)
            return []
        
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
    
