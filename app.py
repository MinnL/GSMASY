from flask import Flask
from flask import request
from flask import render_template
import scholarly

app = Flask(__name__)



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
    limit = 5
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
    return render_template('selectpaper.html', titles=t, abstracts=a, lc=listc)


@app.route('/result', methods=['POST'])
def result():
    sid = request.form['sid']
    sid = sid.split()

    # # get selected abstract
    # sa = []
    # for index, item in enumerate(sid):
    #     sa.append(a[item - 1])
    # # print(sa)
    #
    # # get abstract excluded from selected item
    # x.sort(reverse=True)
    # for index, item in enumerate(x):
    #     a.pop(item - 1)
    #     t.pop(item - 1)
    return render_template('result.html', sid=sid)



def get_abstract():
    sq = input('What do you want to search on Google Scholar?')
    search_query = scholarly.search_pubs_query(sq)

    # create title_list
    t = []
    # create abstract_list
    a = []

    # get google scholar title and abstract
    limit = 500
    for index, item in enumerate(search_query, 1):
        # a.append('PaperID: ' + str(index) + 'Title: ' + item.bib['title'] + 'Abstract: ' + item.bib['abstract'])
        print('PaperID: ' + str(index))
        t.append(item.bib['title'])
        print('Title: ' + item.bib['title'])
        if 'abstract' in item.bib:
            a.append(item.bib['abstract'])
            print('Abstract: ' + item.bib['abstract'])
        else:
            a.append('none')
            print('Abstract: ' + 'none')
        if index == limit:
            break

    return



if __name__ == "__main__":
    app.run
#     (debug=True)




