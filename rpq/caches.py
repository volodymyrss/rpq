    # try cache
    cache_service = None

    if cache_service is not None:
        r = requests.get(cache_service,params=pra)
        if r.status_code == 200:
            result = r.json()
            status = 200
        else:
            result = r.content
            status = 201

        logger.debug("result %s",r)
        logger.debug("result %s",r.content)
