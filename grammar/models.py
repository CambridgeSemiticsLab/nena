from django.db import models
from django.urls import reverse

from treebeard.mp_tree import MP_Node


class Feature(MP_Node):
    name          = models.CharField(max_length=250, unique=False)
    heading       = models.IntegerField(blank=True, null=True)
    group         = models.BooleanField(null=False, default=False)
    fullheading   = models.CharField(max_length=20, blank=True, null=True, editable=False)
    category_list = models.TextField(blank=True, null=True)
    # ^ Pipe (|) separated list of strings, if set must be chosen by related DialectFeature.category

    node_order_by = ['heading']
    CATEGORY_SEPARATOR = '\n'

    def get_absolute_url(self):
        return reverse('grammar:feature-detail', args=[str(self.id)])

    def full_heading(self):
        if self.depth == 1:
            return ''
        elif self.depth == 2:
            return str(self.heading)+'.0'
        else:
            fullheading = [str(a.heading) for a in self.get_ancestors() if a.depth > 1] + [str(self.heading)]
            return '.'.join(fullheading)+'.'

    def __str__(self):
        return "{} {}".format(self.fullheading, self.name)

    def save(self, force_insert=False, force_update=False):
        self.fullheading = self.full_heading()
        super(Feature, self).save(force_insert, force_update)

    def children(self):
        return None if self.get_children_count() == 0 else self.get_children()

    def nodetype(self):
        if self.id in [1, 41, 2236, 2289]: # this seems to be hard-coding ids for rows with depth=1
            return 'root'
        elif self.get_children_count() > 0:
            return 'branch'
        else:
            return 'leaf'

    def list_categories(self):
        list       = self.category_list or ''
        categories = list.split(self.CATEGORY_SEPARATOR)
        return [x.strip() for x in categories]

    def add_category(self, name):
        categories = self.list_categories()
        categories.append(name.strip())
        self.category_list = self.CATEGORY_SEPARATOR.join(set(categories)).strip()

