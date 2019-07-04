from rest_framework.pagination import PageNumberPagination

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


# 自定义分页
class CustomPagination(PageNumberPagination):
    # 每页的数量
    page_size = 20
    # 客户端可以使用此查询参数控制页面。
    page_query_param = 'page'
    # 客户端可以使用此查询参数控制页面大小。
    page_size_query_param = 'page_size'

    # 置为整数以限制客户端可能请求的最大页面大小。
    max_page_size = 100