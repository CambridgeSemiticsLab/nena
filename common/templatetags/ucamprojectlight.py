from django import template

register = template.Library()

@register.filter
def elliptic_range(num_pages, current):
    """
    Produce a list of numbers from 1 to num_pages and including current.
    Long runs of successive numbers will be replaced by "...".
    """
    def gap(start, stop):
        if stop - start < 3:
            return range(start, stop)
        return ["..."]
    ret = []
    if current != 1:
        ret += [1]
        ret += gap(2, current)
    ret += [current]
    if current != num_pages:
        ret += gap(current + 1, num_pages)
        ret += [num_pages]
    return ret
