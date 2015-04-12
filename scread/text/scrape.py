# -*- coding: utf-8 -*-

""" scrape.py: provides functions to retrieve text from web pages. """

import re
from HTMLParser import HTMLParser   
from operator import itemgetter
from common import get_page, strip_html, tags_not_text, tags_inline, tags_blocks


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
       return abs(means[i] - means[j])**6 / (1 + (widths[i] + widths[j])**2) < 0.1

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
   
    avg = average(ys)
    (ns1, ps1) = zip(*filter(lambda (n, (x, y)): y > avg, enumerate(ps)))
    (xs1, ys1) = zip(*ps1)

    cs1 = merge_clusters(xs1, kmeans(xs1, [xs1[0], xs1[-1]] + list(pxs)))
    cs2 = filter_with(lambda y: text_threshold < y + 1e-8, ys1, cs1)
    ns2 = filter_with(lambda c: c in cs2, cs1, ns1)

    return (max(0, min(ns2)-1), min(len(ps), max(ns2)+2))


def get_blocks(page):
    class MyHTMLParser(HTMLParser):

        def __init__(self):
            HTMLParser.__init__(self)
            self._skip_tag = None 
            self._buffer = ''
            self._blocks = []

        def _append(self, data):
            if self._skip_tag == None:
                self._buffer += data

        def _flush(self):
            if len(re.sub(r'\s+', '', strip_html(self._buffer))) > 0:
                self._blocks.append(re.sub(r'(\n\s*)+', '\n', self._buffer))
            self._buffer = ''
            
        def handle_starttag(self, tag, attrs):
            if tag in tags_not_text:
                self._skip_tag = tag

            elif tag in tags_inline:
                self._append('<'+tag+'>') #TODO +attrs

            elif tag in tags_blocks:
                self._flush()

        def handle_endtag(self, tag):
            if tag in tags_not_text:
                if self._skip_tag == tag:
                    self._skip_tag = None

            elif tag in tags_inline:
                self._append('</'+tag+'>') 

        def handle_data(self, data):
            self._append(data)

    parser = MyHTMLParser()
    re_comment = re.compile('<!--.*?-->', flags=re.S|re.I)
    parser.feed(re_comment.sub('', page))
    parser._flush()
    parser.close()

    return parser._blocks


cost = lambda s: len(re.findall('[^.;?!]{2}[.;?!](?= )', strip_html(s)))

def scrape(url):
    blocks = get_blocks(get_page(url))

    n = len(blocks)
    (xs, ys) = [normalize(range(n)), map(cost, blocks)] 
    (l_bound, r_bound) = classify(zip(xs, ys))

    return '<p>' + '</p>\n<p>'.join(blocks[l_bound:r_bound]) + '</p>'

