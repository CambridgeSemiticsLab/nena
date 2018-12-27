from django.db import models
from django.urls import reverse

from treebeard.mp_tree import MP_Node


class Feature(MP_Node):
    name = models.CharField(max_length=250, unique=False)
    heading = models.IntegerField(blank=True, null=True)
    group = models.BooleanField(null=False, default=False)
    fullheading =  models.CharField(max_length=20, blank=True, null=True, editable=False)

    node_order_by = ['heading']

    def get_absolute_url(self):
        return reverse('grammar:feature-detail', args=[str(self.id)])

    def full_heading(self):
        if self.depth == 1:
            return ''
        elif self.depth == 2:
            return str(self.heading)+'.0'
        else:
            fullheading = [str(a.heading) for a in self.get_ancestors() if a.depth > 1] + [str(self.heading)]
        #fullheading = [str(a.heading) for a in self.get_ancestors()]+ [h+'.' for h in str(self.heading)]
            return '.'.join(fullheading)+'.'
    
    def __str__(self):
        return "{} {}".format(self.fullheading, self.name)

    def save(self, force_insert=False, force_update=False):
        self.fullheading = self.full_heading()
        super(Feature, self).save(force_insert, force_update)

    def children(self):
        return None if self.get_children_count() == 0 else self.get_children()

    def nodetype(self):
        if self.id in [1, 41, 2236, 2289]:
            return 'root'
        elif self.get_children_count() > 0:
            return 'branch'
        else:
            return 'leaf'
