# coding=utf-8
from __future__ import unicode_literals


CATALOGFS = {
    'catsql': {'icon': 'fa fa-database', 'text': 'Catalog database export'},
    'bsr': {'icon': 'fa fa-map-signs', 'text': 'Bootstrap Files'},
    'scripts': {'icon': 'fa fa-tags', 'text': 'Scripts'},
}


def catalogfs_get(comp=None):
    if comp is None:
        return {}
    data = CATALOGFS.get(comp, None)
    return data


def catalogfs_get_icon(comp=None):
    if comp is None:
        return ''
    data = CATALOGFS.get(comp, None)
    return data['icon']


def catalogfs_get_text(comp=None):
    if comp is None:
        return ''
    data = CATALOGFS.get(comp, None)
    return data['text']


def catalogfs_getall():
    comps = CATALOGFS.keys()
    data = []
    for c in comps:
        data.append(catalogfs_get(c))
    return data
