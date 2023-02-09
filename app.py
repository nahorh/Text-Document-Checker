from flask import *
import re
import nltk
import fitz
from PyPDF2 import PdfReader
import heapq
from flask_restful import Api,Resource
import bs4 as bs
import urllib.request
from urllib.error import HTTPError

app=Flask(__name__)
api=Api(app)

class SummarizePDF(Resource):
    def post(self):
        file=request.files['data_file']
        file.save("static/uploads/data.pdf")
        doc = fitz.open('static/uploads/data.pdf')
        article_text = ""
        for page in doc:
            article_text+=page.get_text()

        # Removing Square Brackets and Extra Spaces
        article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
        article_text = re.sub(r'\s+', ' ', article_text)

        # Removing special characters and digits
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

        sentence_list = nltk.sent_tokenize(article_text)

        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        a = 20
        summary_sentences = heapq.nlargest(a, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return jsonify({"status":200,"result":summary})

class SummarizeText(Resource):
    def post(self):
        data=request.get_json()
        text=data['copied-text']
        # Removing Square Brackets and Extra Spaces
        text = re.sub(r'\[[0-9]*\]', ' ', text)
        text = re.sub(r'\s+', ' ', text)

        # Removing special characters and digits
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', text )
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

        sentence_list = nltk.sent_tokenize(text)

        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        a = 20
        summary_sentences = heapq.nlargest(a, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return jsonify({"status":200,"result":summary})
        pass
class SummarizeWeb(Resource):
    def post(self):
        try:
            data=request.get_json()
            link=data['link']
            scraped_data = urllib.request.urlopen(link)
            article = scraped_data.read()
            parsed_article = bs.BeautifulSoup(article,'html.parser')
            paragraphs = parsed_article.find_all('p')
            article_text = ""
            for p in paragraphs:
                article_text += p.text

            # Removing Square Brackets and Extra Spaces
            article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
            article_text = re.sub(r'\s+', ' ', article_text)

            # Removing special characters and digits
            formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
            formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

            sentence_list = nltk.sent_tokenize(article_text)

            stopwords = nltk.corpus.stopwords.words('english')

            word_frequencies = {}
            for word in nltk.word_tokenize(formatted_article_text):
                if word not in stopwords:
                    if word not in word_frequencies.keys():
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1

            sentence_scores = {}
            for sent in sentence_list:
                for word in nltk.word_tokenize(sent.lower()):
                    if word in word_frequencies.keys():
                        if len(sent.split(' ')) < 30:
                            if sent not in sentence_scores.keys():
                                sentence_scores[sent] = word_frequencies[word]
                            else:
                                sentence_scores[sent] += word_frequencies[word]

            a = 20
            summary_sentences = heapq.nlargest(a, sentence_scores, key=sentence_scores.get)
            summary = ' '.join(summary_sentences)
            return jsonify({"status":200,"result":summary})
        except HTTPError as e:
            return jsonify({"status":403,"result":""})
        
@app.route("/", methods=['GET'])
def index():
    return render_template('base.html')
    
@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login/home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('register/home.html')
    
@app.route('/summarize',methods=['GET','POST'])
def summarize():
    if request.method == 'GET':
        return render_template('summarize/home.html')
    else:
        file=request.files['data_file']
        # file.save(url_for('static',filename="uploads/data.pdf"))
        file.save("static/uploads/data.pdf")
        doc = fitz.open('static/uploads/data.pdf')
        article_text = ""
        for page in doc:
            article_text+=page.get_text()

        # Removing Square Brackets and Extra Spaces
        article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)
        article_text = re.sub(r'\s+', ' ', article_text)

        # Removing special characters and digits
        formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )
        formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

        sentence_list = nltk.sent_tokenize(article_text)

        stopwords = nltk.corpus.stopwords.words('english')

        word_frequencies = {}
        for word in nltk.word_tokenize(formatted_article_text):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        a = 20
        summary_sentences = heapq.nlargest(a, sentence_scores, key=sentence_scores.get)
        summary = ' '.join(summary_sentences)
        return render_template('summarize/home.html',summary=summary)
        pass

api.add_resource(SummarizePDF,'/summarize/pdf')
api.add_resource(SummarizeText,'/summarize/text')
api.add_resource(SummarizeWeb,'/summarize/web')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)