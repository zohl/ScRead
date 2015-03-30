import init 
import sys
import operator
from scread.text.scrape import get_blocks, classify, normalize, average
from scread.text.common import get_page

  
urls = [
  ( 9, 38, 'http://aeon.co/magazine/philosophy/is-cowardice-a-form-of-bravery/')
, (14, 32, 'http://arstechnica.com/science/2015/02/the-powerful-cheat-for-themselves-the-powerless-cheat-for-others/')
, ( 7, 97, 'http://bbc.co.uk/news/resources/idt-bbb9e158-4a1b-43c7-8b3b-9651938d4d6a')
, ( 3, 26, 'http://blogs.valvesoftware.com/economics/it-all-began-with-a-strange-email/')
, ( 8, 40, 'http://businessinsider.com/polyphasic-sleep-schedules-and-benefits-2013-10')
, ( 4, 23, 'http://economist.com/news/leaders/21641204-john-micklethwait-who-has-edited-newspaper-2006-leaves-today-these-are-his-parting')
, ( 3, 20, 'http://elle.com/culture/career-politics/advice/a2521/burnout-essay/')
, (26, 44, 'http://fivethirtyeight.com/datalab/a-cheat-sheet-for-comeys-speech-on-race-and-policing/')
, (21, 33, 'http://forbes.com/sites/amadoudiallo/2014/12/15/you-hate-passwords-but-hackers-love-them/')
, ( 8, 21, 'http://foxnews.com/opinion/2015/02/12/is-our-constitution-just-worthless-piece-paper/')
, (19, 24, 'http://gizmodo.com/men-who-post-selfies-online-show-signs-of-psychopathy-1678809922')
, ( 4, 23, 'http://joelonsoftware.com/items/2008/05/01.html')
, ( 7, 49, 'http://m.bbc.com/news/health-30742774')
, ( 8, 13, 'http://m.huffpost.com/us/entry/6585524')
, (28, 58, 'http://m.nautil.us/issue/15/turbulence/can-you-die-from-a-broken-heart')
, ( 8, 22, 'http://wired.com/2014/10/microsoft-windows-will-run-docker/')
, (11, 27, 'http://mashable.com/2014/12/17/bad-jobs-mental-health/')
, (16, 20, 'http://mobile.nytimes.com/2014/01/20/opinion/chinas-web-junkies.html?referrer=')
, (27, 76, 'http://motherboard.vice.com/read/how-to-teach-computer-science-in-north-korea')
, ( 8, 39, 'http://newyorker.com/magazine/2013/02/04/life-at-the-top')
, ( 8, 22, 'http://qz.com/231313/children-arent-worth-very-much-thats-why-we-no-longer-make-many/')
, ( 9, 24, 'http://sciencedaily.com/releases/2015/01/150123081725.htm?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+sciencedaily%2Fcomputers_math%2Fcomputer_programming+%28Computer+Programming+News+--+ScienceDaily%29')
, (27, 82, 'http://techcrunch.com/2015/01/21/farewell-sheriff/?ncid=rss&utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Techcrunch+%28TechCrunch%29')
, (11, 14, 'http://theguardian.com/lifeandstyle/2014/sep/19/column-change-life-empathy-oliver-burkeman')
, (20, 91, 'http://thenextweb.com/entrepreneur/2014/12/25/14-things-better-love-becoming-entrepreneur/')
, (28, 48, 'http://washingtonpost.com/blogs/the-switch/wp/2015/01/28/bill-gates-on-dangers-of-artificial-intelligence-dont-understand-why-some-people-are-not-concerned/?tid=pm_business_pop')
, ( 4, 16, 'http://www.economist.com/news/business/21620197-getting-top-much-do-how-you-look-what-you-achieve-look-leader')
]

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
    (l_bound, r_bound, url) = urls[i]

    # f = open('./urls_data/data_%d.html' % i)
    # page = f.read()
    # f.close()

    page = get_page(url)

    blocks = map(operator.itemgetter(2), get_blocks(page))
    n = len(blocks)
    (xs, ys) = [normalize(range(n)), map(len, blocks)]

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
    if action == 'stat':
        print '%2d : %s : %.04f' % (i, 'OK' if all_captured else 'FA', accuarcy)

    # extracted blocks
    if action == 'blocks':
        print '\n'.join(map(lambda (n, t): '%03d: %s' % (n, t), enumerate(blocks)))
        print '---------\n\n\n\n\n-----------'

    return accuarcy


def test_classify():
    res = map(scrape, range(len(urls)))
    assert average(res) < 0.3


if len(sys.argv) >= 2:
    action = sys.argv[1][2:]
    if action in ['plot', 'stat', 'blocks']:
        if len(sys.argv) >= 3:
            scrape(int(sys.argv[2]), action)
        else:
            avg_acc = average(map(lambda i: scrape(i, action), range(len(urls))))
            if action == 'stat':
                print 'AVG: %f' % avg_acc



# f = open('scraping/data_0.html')
# page = f.read()
# f.close()
# 
# for (tag, attr, text) in get_blocks(page):
#     print text 
#     print ' --- '
