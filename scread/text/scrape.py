# -*- coding: utf-8 -*-

""" scrape.py: provides functions to retrieve text from web pages. """

import re
from operator import itemgetter
from common import get_page

SENTENCE_THRESHOLD = 100


filter_with = lambda p, xs, ys: zip(*filter(lambda (x, y): p(x), zip(xs, ys)))[1]

def normalize(xs):
    m = max(xs)
    return map(lambda x: x*1.0/m, xs)

def average(xs):
    assert len(xs) > 0
    return sum(xs)*1.0/len(xs)

def nearest(x0, means):
    dists = sorted(map(lambda (k, x): (abs(x - x0), k), enumerate(means)))
    return dists[0][1]

def cluster(xs, cs, k):
    result = filter(lambda (x, c): c == k, zip(xs, cs))
    return [] if len(result) == 0 else zip(*result)[0]


def kmeans(xs, means):
    cs = []

    for i in range(24):
        cs = map(lambda x: nearest(x, means), xs)
        clusters = map(lambda k: cluster(xs, cs, k), range(len(means)))
        means = map(average, filter(lambda cl: len(cl) > 0, clusters))

    return cs


def merge_clusters(xs, cs):

    n = max(cs) + 1
    clusters = map(lambda k: cluster(xs, cs, k), range(n))
    widths = map(lambda cl: (max(cl) - min(cl)), clusters)
    means = map(average, clusters)
    
    def is_near(i, j):
       return abs(means[i] - means[j])**4 / (1 + (widths[i] + widths[j])) < 0.1

    adjs = map(lambda i: map(lambda j: is_near(i, j), range(i)), range(n))

    links = map(lambda (i, adj): i if 1 not in adj else adj.index(1), enumerate(adjs))
    for (i, c) in enumerate(links):
        links[i] = links[c]
    
    return map(lambda c: links[c], cs)



def get_peaks(ps):
    threshold = max(zip(*ps)[1]) - 1e-8
    return filter(lambda (x, y): y > threshold, ps)


def classify(ps):
    (xs, ys) = zip(*ps)
    (pxs, pys) = zip(*get_peaks(ps))
    text_threshold = min(pys)
    
    (ns1, ps1) = zip(*filter(lambda (n, (x, y)): y > SENTENCE_THRESHOLD, enumerate(ps)))
    (xs1, ys1) = zip(*ps1)

    cs1 = merge_clusters(xs1, kmeans(xs1, [xs1[0], xs1[-1]] + list(pxs)))
    cs2 = filter_with(lambda y: text_threshold < y + 1e-8, ys1, cs1)
    ns2 = filter_with(lambda c: c in cs2, cs1, ns1)

    return (max(0, min(ns2)-1), min(len(ps), max(ns2)+2))



def get_blocks(page):
    
    mk_regexp = lambda tmpl, *tags: re.compile(tmpl % '|'.join(tags), flags=re.S|re.I)

    re_not_text = mk_regexp('<(?P<tag>%s)(?P<attr> [^<>]*)?(/>|>(?P<text>.*?)</(?P=tag)>)'
                         , 'style', 'script', 'object', 'img', 'button', 'input', 'textarea')

    re_inlines = mk_regexp('</?(?P<tag>%s)(?P<attr> [^<>]*)?>'
                         , 'b', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'cite'
                         , 'code', 'dfn', 'em', 'kbd', 'strong', 'samp', 'var', 'a'
                         , 'bdo', 'br', 'q', 'span', 'sub', 'sup')

    re_blocks = mk_regexp('<(?P<tag>%s)(?P<attr> [^<>]*)?>(?P<text>[^<>]*?)</(?P=tag)>'
                        , 'dd', 'div', 'p', 'pre', 'h[1-6]', 'ol', 'ul', 'table')

    not_empty = lambda m: (lambda text:
                           text is not None
                       and len(text) > 0
                       and (re.match(r'^[ \n]*$', text) is None))(m.group('text'))

    page = re_inlines.sub('', re_not_text.sub('', page))

    return map(lambda m: map(lambda s: m.group(s), ['tag', 'attr', 'text'])
             , filter(not_empty, re_blocks.finditer(page)))


def scrape(url):
    blocks = map(itemgetter(2), get_blocks(get_page(url)))
    n = len(blocks)
    (xs, ys) = [normalize(range(n)), map(len, blocks)]

    (l_bound, r_bound) = classify(zip(xs, ys))
    return '<p>' + '</p>\n<p>'.join(blocks[l_bound:r_bound]).decode('utf-8') + '</p>'

