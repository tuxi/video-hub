def create_md5():
    '''
    通过MD5的方式创建
    :return:
    '''

    import time
    time_str = str(time.time())
    try:
        import md5
        hash = md5.new(time_str).hexdigest()
    except ImportError as e:
        from hashlib import md5
        hash = md5(time_str.encode()).hexdigest()

    return hash


def generatingUserName():
    return "alpface" + create_md5()