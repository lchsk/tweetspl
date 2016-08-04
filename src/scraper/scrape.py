# -*- coding: utf-8 -*-
import urllib
import re
import random
import sys
import re
import string
reload(sys)
sys.setdefaultencoding("utf-8")
from bs4 import BeautifulSoup
import unicodedata

def get_text_and_stars(book_id):
    # book_id = 4484
    comments_url = 'http://lubimyczytac.pl/ksiazka/{0}'.format(book_id)

    html = urllib.urlopen(comments_url).read()
    soup = BeautifulSoup(html, 'html.parser')

    reviews_html = soup.find_all('div', class_='review')
    reviews = []

    for r in reviews_html:
        stars = r.find_all('div', class_='rating-star-holder')
        stars_cnt = 0
        for star in stars:
            if 'rating-on' in str(star):
                stars_cnt += 1

        if stars_cnt > 0:
            # text = r.find_all('div', class_='reviewContent')
            text = r.find('p', 'regularText')

            if text:
                text = text.get_text().replace(
                    '\n', ''
                ).replace(
                    u'przeczytaj całą opinię »', u''
                ).strip()
                reviews.append(
                    (stars_cnt, text)
                )
    return reviews



def remove_accents(s):
    tmp = u''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )

    tmp = tmp.replace('ł', 'l')

    return tmp

def transform(lines):
    re_all_but_letters = re.compile(r'[^\w ]+', re.UNICODE)
    re_single_spaces = re.compile(r'\s+', re.UNICODE)
    transformed = []

    for line in lines:
        line = remove_accents(line)
        line = line.lower()
        line = re_all_but_letters.sub('', line)
        line = re_single_spaces.sub(' ', line)

        result = []

        words = line.split()

        for i, word in enumerate(words[0:-1]):
            result.append(word)
            result.append(u'{0}__{1}'.format(word, words[i + 1]))

        random.shuffle(result)
        transformed.append(u' '.join(result))

    return transformed

def run():
    product_id = random.randint(1, 300000)
    return get_text_and_stars(product_id)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Pass a parameter'
    else:
        if sys.argv[1] == 'test':
            get_text_and_stars(1)

        elif sys.argv[1] == 'transform_raw':
            negative = []
            positive = []

            neg_file = open('data.negative', 'w')
            pos_file = open('data.positive', 'w')

            with open('test.txt') as f:
                for line in f:
                    try:
                        mark, text = line.split('||')
                    except ValueError:
                        continue

                    if int(mark) <= 5:
                        negative.append(text.decode('utf-8'))
                    else:
                        positive.append(text.decode('utf-8'))

            negative = transform(negative)
            positive = transform(positive)

            # Ensure both datasets are of the same length
            length = min(len(negative), len(positive))

            for i, line in enumerate(negative[:length]):
                neg_file.write(u'{0}\n'.format(line))

            for i, line in enumerate(positive[:length]):
                pos_file.write(u'{0}\n'.format(line))

            neg_file.close()
            pos_file.close()

        elif sys.argv[1] == 'show_mark':
            with open('test.txt') as f:
                for line in f:
                    try:
                        mark, text = line.split('||')
                    except ValueError:
                        continue

                    if int(mark) == int(sys.argv[2]):
                        print text

        elif sys.argv[1] == 'stats':
            with open('test.txt') as f:
                pos_cnt = 0
                neg_cnt = 0

                for line in f:
                    try:
                        mark, text = line.split('||')
                    except ValueError:
                        continue

                    if int(mark) <= 5:
                        neg_cnt += 1
                    else:
                        pos_cnt += 1

                print '+: {0}\n-: {1}'.format(pos_cnt, neg_cnt)

        elif sys.argv[1] == 'download':
            with open('test.txt', 'a') as f:
                for i in xrange(0, 5000):
                    print 'Iteration #{0}'.format(i + 1)
                    reviews = run()
                    if reviews:
                        print 'Saving {0} reviews'.format(len(reviews))
                        for mark, r in reviews:
                            f.write(
                                u'{mark}||{review}\n'.format(
                                    mark=mark,
                                    review=r
                                ).encode('utf-8')
                            )
        elif sys.argv[1] == 'divide':
            current_file = None

            with open('raw_output.txt') as f:
                for i, line in enumerate(f):
                    if current_file is None or i % 100 == 0:
                        if current_file:
                            current_file.close()
                        current_file = open('divided/raw_{0}.txt'.format(i // 100), 'w')

                    current_file.write(line)

            if current_file:
                current_file.close()
