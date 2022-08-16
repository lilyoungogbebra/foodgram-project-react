from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    '''Пагинация пользователей по параметру limit.'''
    page_size_query_param = 'limit'