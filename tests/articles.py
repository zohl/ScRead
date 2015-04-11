# -*- coding: utf-8 -*-

import init 

import os
from scread.text.common import get_page, strip_html

def get_article(n):
    fn = './cache_data/article_%d.html' % n

    if not os.path.isfile(fn):
        f = open(fn, 'w')
        f.write(get_page(articles[n][0]).encode('utf-8'))
        f.close()

    f = open(fn, 'r')
    page = f.read().decode('utf-8')
    f.close()

    return page


def get_article_bounds(n, blocks):
    (_1, l_text, r_text) = articles[n]

    assert len(blocks) > 0

    sblocks = map(strip_html, blocks)
    get_matches = lambda text: filter(lambda (n, b): b.find(text) != -1, enumerate(sblocks))
    
    l_matches = get_matches(l_text)
    assert len(l_matches) > 0
    assert len(l_matches) == 1
    
    r_matches = get_matches(r_text)
    assert len(r_matches) > 0
    assert len(r_matches) == 1
    
    l_bound = l_matches[0][0]
    r_bound = r_matches[-1][0]
    assert l_bound <= r_bound
    
    return (l_bound, r_bound)

articles = map(lambda xs: map(lambda x: x.decode('utf-8'), xs), [
    ('http://aeon.co/magazine/philosophy/is-cowardice-a-form-of-bravery/',
     'One coward may lose a battle, one battle may lose ',
     'cy. Pondering cowardice can help us overcome them.'),

    ('http://arstechnica.com/science/2015/02/the-powerful-cheat-for-themselves-the-powerless-cheat-for-others/',
     'Research has previously shown that upper-class ind',
     'he self or for others, to discourage the behavior.'),

    ('http://bigthink.com/neurobonkers/what-has-been-the-real-world-impact-of-neuromyths',
     'A paper published in Nature Reviews Neuroscience l',
     'r teachers and policy makers to do their homework.'),

    ('http://blog.erratasec.com/2015/02/technical-terms-are-not-ambiguous.html',
     'I see technical terms like "interference" and "aut',
     'ted by the statute without a technical discussion.'),

    ('http://blog.erratasec.com/2015/02/technical-terms-are-not-ambiguous.html?m=1',
     'Take for example the law that forbids causing radi',
     'ted by the statute without a technical discussion.'),

    ('http://blogs.valvesoftware.com/economics/it-all-began-with-a-strange-email/',
     'It was late at night in October of last year when ',
     'deas regarding Valve’s various social ‘economies’.'),

    ('http://blogs.wsj.com/washwire/2015/02/20/how-latest-snowden-leak-is-headache-for-white-house/?mod=WSJ_article_EditorsPicks_0',
     'Former National Security Agency contractor Edward ',
     'ry safe, but also to protect our civil liberties.”'),

    ('http://edition.cnn.com/2014/02/20/opinion/schneier-nsa-too-big/index.html',
     'The NSA has become too big and too powerful.  What',
     ' tame the enormous beast that the NSA has become. '),

    ('http://fivethirtyeight.com/datalab/a-cheat-sheet-for-comeys-speech-on-race-and-policing/',
     'FBI Director James Comey’s Thursday speech on race',
     'e. But there’s a clear need for better statistics.'),

    ('http://gizmodo.com/men-who-post-selfies-online-show-signs-of-psychopathy-1678809922',
     'A study surveying the social media habits of 800 m',
     'create them. [Ohio State University via PetaPixel]'),

    ('http://jakeseliger.com/2014/09/14/all-american-fiction-is-young-adult-fiction-discuss/',
     'Via Twitter Hollis Robbins offers a prompt: “‘[A]l',
     ' adult fiction, that may be a sign of progress.***'),

    ('http://jaxenter.com/slow-programming-112923.html',
     'When it comes to successful software, does it pay ',
     'the race. Fast and furiously or slow and steadily?'),

    ('http://jaxenter.com/the-deal-with-older-programmers-114615.html',
     'For a career that involves a lot of sitting, it’s ',
     'e. Youth alone as value shouldn’t be the standard.'),

    ('http://joelonsoftware.com/items/2008/05/01.html',
     'It was seven years ago today when everybody was ge',
     'xt week. And dammit foosball doesn\'t play itself.'),

    ('http://knowledgenuts.com/2013/10/06/the-mysterious-children-with-green-skin/',
     'In the 12th century, two children were reportedly ',
     ' Even with that, we’ll never fully know the truth.'),

    ('http://knowledgenuts.com/2014/04/09/some-animals-can-consume-knowledge-by-eating-other-animals/',
     'The above statement got everyone looking for proof',
     'tinue to this day and continue to raise eyebrows. '),

#   ('http://m.bbc.com/news/health-30742774',
#    'Dr Tony Perry, a pioneer in cloning, has announced',
#    'uld entail" for there to be any change in the law.'),

    ('http://m.bbc.com/news/magazine-29817519',
     'Tea or coffee is often the favoured brew for those',
     ' of prolonged, uncontrolled use are likely to be."'),

    ('http://m.nautil.us/issue/15/turbulence/can-you-die-from-a-broken-heart',
     'Ruth and Harold “Doc” Knapke met in elementary sch',
     'l chaos can tip the scales toward an untimely end.'),

    ('http://mashable.com/2014/12/17/bad-jobs-mental-health/',
     'There can be no doubt that the job market has been',
     'ay be that "any job" may not be a good job at all.'),

    ('http://mikethecoder.tumblr.com/post/13921045927/ted-dziuba-taco-bell-programming',
     'If you haven’t read Ted Dziuba’s post on Taco Bell',
     'you’re more aware of the things you don’t know :-)'),

    ('http://mobile.nytimes.com/2014/01/20/opinion/chinas-web-junkies.html?referrer&_r=0',
     'Compulsive Internet use has been categorized as a ',
     ' technology and provide help to those who need it.'),

    ('http://motherboard.vice.com/read/an-ad-company-is-flying-surveillance-drones-over-los-angeles',
     '​An ad company’s drones have been quietly collecti',
     'relevant ads, which helps them stay free forever."'),

    ('http://motherboard.vice.com/read/how-to-teach-computer-science-in-north-korea',
     'For a computer scientist, Will Scott has a pretty ',
     ' happy and unhappy people within any population.​"'),

    ('http://nymag.com/scienceofus/2014/09/psychology-of-the-start-up-world.html?mid=twitter_nymag',
     'At first, I found it strange that I had gotten so ',
     'start-up founders, but for the rest of us, too.'),

    ('http://qz.com/231313/children-arent-worth-very-much-thats-why-we-no-longer-make-many/',
     'The nineteenth and twentieth centuries have been c',
     'ly attractive proposition than making a new slave.'),

    ('http://techcrunch.com/2015/01/21/farewell-sheriff/?ncid=rss',
     'Lolcats, Anonymous, and countless Internet memes a',
     ' Clearly the ship should sail without the captain.'),

    ('http://thebeaker.org/post/111556346991/how-rectal-thermometers-and-antarctic-excursions',
     'Temperatures have plummeted in Connecticut, with w',
     'per attire, going outside, and avoiding frostbite.'),

    ('http://thediplomat.com/2014/10/kim-jong-uns-sister-takes-control-in-north-korea/',
     'According to a new report by a Seoul think tank, K',
     '-chul, a spokesman of the Ministry of Unification.'),

    ('http://thenextweb.com/entrepreneur/2014/12/25/14-things-better-love-becoming-entrepreneur/',
     'Imagine somebody asked you to write on a piece of ',
     ' other people who will go on the journey with you.'),

    ('http://tocaboca.com/magazine/kids-who-are-not-playful/',
     'Playful kids are spontaneous and creative. They te',
     'oth kids and adults, it’s time to be more playful!'),

    ('http://www.bbc.co.uk/news/resources/idt-bbb9e158-4a1b-43c7-8b3b-9651938d4d6a',
     'amazing that the amount of news that happens in th',
     'insightful and independent - is greater than ever.'),

    ('http://www.businessinsider.com/polyphasic-sleep-schedules-and-benefits-2013-10',
     'A normal person spends about a third of their live',
     'efits of limited sleep with none of the downsides.'),

    ('http://www.businessinsider.com/tony-horton-weight-loss-advice-2015-4',
     'Tony Horton is one of the most visible people — if',
     't deal with that you’re always going to struggle."'),

    ('http://www.economist.com/news/business/21620197-getting-top-much-do-how-you-look-what-you-achieve-look-leader',
     'IN GORILLA society, power belongs to silverback ma',
     'e who choose leaders still seem to think this way.'),

    ('http://www.economist.com/news/leaders/21641204-john-micklethwait-who-has-edited-newspaper-2006-leaves-today-these-are-his-parting',
     'THIS newspaper churlishly deprives its editors of ',
     'ds. And that is my last, best reason for optimism.'),

    ('http://www.elle.com/culture/career-politics/advice/a2521/burnout-essay/',
     'A few years ago, after shooting up the career ladd',
     'st. Something we lived with before we knew better.'),

    ('http://www.engadget.com/2015/02/19/nsa-gchq-gemalto-hack/',
     'You might not have heard the name "Gemalto" before',
     'e to make it easy for any potentially prying eyes.'),

    ('http://www.forbes.com/sites/amadoudiallo/2014/12/15/you-hate-passwords-but-hackers-love-them/',
     'been creating passwords since the dawn of the Inte',
     'venient and far safer than what we’re using today.'),

    ('http://www.foxnews.com/opinion/2015/02/12/is-our-constitution-just-worthless-piece-paper/',
     'President George W. Bush was fond of saying that “',
     'onstitution has become a worthless piece of paper.'),

    ('http://www.huffingtonpost.com/katharine-zaleski/the-artist-behind-the-sex_b_6585524.html',
     'On Friday I interviewed Edel Rodriguez, the artist',
     'Print will evolve, but it will never die.'),

    ('http://www.lockedowndesign.com/help-from-people-in-your-industry/',
     'Today, Matt Medeiros published an article called H',
     'iously, they are more likely to help you later on.'),

    ('http://www.medicalnewstoday.com/articles/289995.php',
     'Scientists believe they have discovered the neuron',
     'hed a "video abstract" of their study at YouTube:'),

    ('http://www.newyorker.com/culture/cultural-comment/suicide-crime-loneliness',
     'Every forty seconds, someone commits suicide. In t',
     'e aloneness in each of us is, finally, inviolable.'),

    ('http://www.newyorker.com/magazine/2013/02/04/life-at-the-top',
     'Shortly after dawn one December morning, Bob Menze',
     'eward, we get to go to the top and start again.” ♦'),

    ('http://www.nytimes.com/1988/02/25/us/brain-wound-eliminates-man-s-mental-illness.html',
     'A mentally ill young man who',
     'tine of Massachusetts General Hospital in Boston. '),

    ('http://www.randalolson.com/2014/09/13/who-are-the-climate-change-deniers/',
     'It seems that every 6 months, we see the news ligh',
     'hout alienating the average American conservative?'),

    ('http://www.sciencealert.com/features/20143009-26257.html',
     'On 27 August 1883, the Earth made the loudest nois',
     ' it together a whole lot better than I would have:'),

    ('http://www.sciencedaily.com/releases/2014/09/140925132559.htm   ',
     'People who practice yoga and meditation long term ',
     'er of people who could benefit from our research."'),

    ('http://www.sciencedaily.com/releases/2015/01/150123081725.htm',
     'IT researchers have developed a programming langua',
     's and Type-Directed Synthesis, on 23 January 2015.'),

    ('http://www.theguardian.com/lifeandstyle/2014/sep/19/column-change-life-empathy-oliver-burkeman',
     'What the world really needs, according to the Yale',
     'But wouldn\'t you rather I did something about it?'),

    ('http://www.washingtonpost.com/blogs/the-switch/wp/2015/01/28/bill-gates-on-dangers-of-artificial-intelligence-dont-understand-why-some-people-are-not-concerned/?tid=pm_business_pop',
     'Bill Gates is a passionate technology advocate (bi',
     't Research are focused on artificial intelligence.'),

    ('http://www.wired.com/2014/10/microsoft-windows-will-run-docker/',
     'The next big thing in cloud computing doesn’t work',
     'inux world. But now, the company realizes it must.'),

    ('https://hbr.org/2014/10/stop-being-so-positive/',
     'We’ve all heard a great deal about the power of po',
     'es will it consistently produce desirable results.'),

    ('https://hbr.org/2014/10/what-you-eat-affects-your-productivity/',
     'Think back to your most productive workday in the ',
     'making healthy eating the easiest possible option.'),

    ('https://news.yahoo.com/anti-facebook-social-network-gets-viral-surge-044242310.html;_ylt=AwrBJR.oMihUexoAqzjQtDMD',
     'Washington (AFP) - In a matter of days, the new so',
     'cussions of this toxic system were not so tragic."')
])

MAX_ARTICLES = len(articles)
