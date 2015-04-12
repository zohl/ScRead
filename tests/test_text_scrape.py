# -*- coding: utf-8 -*-

import init 
import os
import re
import sys
import operator
from scread.text.scrape import get_blocks, classify, normalize, average, cost
from scread.text.common import strip_html
from articles import get_article, get_article_bounds, MAX_ARTICLES

plot_template = """
%s

png(file=fn, width=800, height=450)
par(pch=19)
plot(xs, ys, col=c("black", "red", "green", "gray", "purple", "blue")[cs+1], main=msg)

par(lwd=3)
abline(v=c(l_bound, r_bound))
dev.off()
"""

to_vector = lambda xs: 'c(' + ', '.join(map(str, xs)) + ')'

def scrape(i, action = 'test'):
    def output(blocks):
        f = open('output.dat', 'w')
        for d in enumerate(map(strip_html, blocks)):
            print >> f, ("%03d: %s" % d).encode('utf-8')
        f.close()
        
    page = get_article(i)
    blocks = get_blocks(page)
    try:
        (l_bound, r_bound) = get_article_bounds(i, blocks)
    finally:
        pass
        #output(blocks)

    n = len(blocks)
    (xs, ys) = [normalize(range(n)), map(cost, blocks)] 

    (cl_bound, cr_bound) = classify(zip(xs, ys))
    all_captured = (l_bound >= cl_bound and r_bound <= cr_bound)
    accuarcy = (((l_bound - cl_bound) + (cr_bound - r_bound))*1.0/n) if all_captured else 1
    
    # for py.test
    if action == 'test':
        assert all_captured

    # R script for visual representation
    if action == 'plot':
        cs = map(lambda x: int(cl_bound <= x and x <= cr_bound), range(n))
        print plot_template % '\n'.join([
            'cs <- ' + to_vector(cs)
            , 'xs <- ' + to_vector(xs)
            , 'ys <- ' + to_vector(map(lambda y: y*y, ys))
            , 'l_bound <- %s/%s' % (l_bound, str(n))
            , 'r_bound <- %s/%s' % (r_bound, str(n))
            , 'msg <- "%s (%f)"' % ('OK' if all_captured else 'FAIL', accuarcy)
            , 'fn <- "./data_%d.png"' % i    
        ])
        
    # an overview 
    if action == 'stats':
        print '%2d : %s : %.04f' % (i, 'OK' if all_captured else 'FA', accuarcy)

    return accuarcy


def test_classify():
    res = map(scrape, range(MAX_ARTICLES))
    assert average(res) < 0.4


if len(sys.argv) >= 2:
    action = sys.argv[1][2:]
    if action in ['test', 'plot', 'stats']:
        if len(sys.argv) >= 3:
            scrape(int(sys.argv[2]), action)
        else:
            avg_acc = average(map(lambda i: scrape(i, action), range(MAX_ARTICLES)))
            if action == 'stats':
                print 'AVG: %f' % avg_acc

