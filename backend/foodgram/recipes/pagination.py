from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    '''Пагинация рецептов по параметру limit.'''
    page_size_query_param = 'limit'
