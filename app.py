from flask import Flask
from flask import request
from flask import render_template
from flask import session
import scholarly
from sklearn.feature_extraction import text
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from stemming.porter2 import stem

app = Flask(__name__)
app.secret_key = "super secret key"



@app.route('/')
def search():
    return render_template('gssearch.html')


@app.route('/selectpaper', methods=['POST'])
def select():
    sq = request.form['sq']
    search_query = scholarly.search_pubs_query(sq)

    # create book id list
    i = []
    # create title_list
    t = []
    # create abstract_list
    a = []

    # get google scholar title and abstract
    limit = 15
    for index, item in enumerate(search_query, 1):
        # a.append('PaperID: ' + str(index) + 'Title: ' + item.bib['title'] + 'Abstract: ' + item.bib['abstract'])
        # print('PaperID: ' + str(index))
        i.append(index)
        t.append(item.bib['title'])
        # print('Title: ' + item.bib['title'])
        if 'abstract' in item.bib:
            a.append(item.bib['abstract'])
            # print('Abstract: ' + item.bib['abstract'])
        else:
            a.append('none')
            # print('Abstract: ' + 'none')
        if index == limit:
            break
    listc = [[x, y, z] for x, y, z in zip(i, t, a)]
    session['abstract'] = a
    session['title'] = t
    return render_template('selectpaper.html', titles=t, abstracts=a, lc=listc)


@app.route('/result', methods=['POST'])
def result():
    sid = request.form['sid']
    sid = sid.split()
    sid = [int(i) for i in sid]
    a = session.get('abstract')
    t = session.get('title')

    # get selected abstract
    sa = []
    for index, item in enumerate(sid):
        sa.append(a[item - 1])

    # get abstract excluded from selected item
    sid.sort(reverse=True)
    for index, item in enumerate(sid):
        a.pop(item - 1)
        t.pop(item - 1)
    #
    # make non-selected articles a data frame for calculation
    ta_df = pd.DataFrame({'Title': t, 'Abstract': a})

    # combine 2 lists to one
    s = " "
    sa = s.join(sa)  # make all selected abstracts into one
    ca = a
    ca.append(sa)  # append the selected abstracts
    #
    # Stopwords
    my_additional_stop_words = ["author", "and", "of", "the", "research", "\n"]
    stop_words = text.ENGLISH_STOP_WORDS.union(my_additional_stop_words)
    #
    # STEM
    ca = [[stem(word) for word in sentence.split(" ")] for sentence in ca]
    y = len(ca)
    for i in range(0, y):
        ca[i] = " ".join(ca[i])

    # build tf-idf matrix
    tfidf = text.TfidfVectorizer(input=ca, stop_words=stop_words, analyzer='word', lowercase=True)
    matrix = tfidf.fit_transform(ca)

    # calculate similarity score
    sim_unigram = cosine_similarity(matrix)

    # build function to get similar score for all articles by locating them
    def get_similar_papers(x):
        return ta_df.loc[np.argsort(-x)]

    recomPaper = get_similar_papers(sim_unigram[-1])

    sim_unigram[-1][::-1].sort()  # descending
    # # sim_unigram[-1].sort() #ascending

    recomPaper["Similar_score"] = sim_unigram[-1]

    # get the 50 papers with highest similarity
    recomPaper50 = recomPaper[:51]
    recomPaper50 = recomPaper50.dropna().reset_index(drop=True)
    tl = recomPaper50['Title'].tolist()
    al = recomPaper50['Abstract'].tolist()
    sl = recomPaper50['Similar_score'].tolist()
    listc = [[x, y, z] for x, y, z in zip(tl, al, sl)]
    #
    # output file
    # recomPaper50.to_csv("recom50papers.csv")

    return render_template('result.html', sid=sid, a=a, t=t, result=recomPaper50, lc=listc)



if __name__ == "__main__":
    app.run(debug=True)




