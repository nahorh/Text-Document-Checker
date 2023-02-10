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
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app=Flask(__name__)
api=Api(app)

class Summarizer(Resource):
    def post(self):
        try:
            data=request.get_json()
            text=data['text']
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
            if len(summary) ==0:
                return jsonify({"status":200,"result":"Nothing To Summarize"})
            return jsonify({"status":200,"result":summary})
        except:
            return jsonify({"status":400,"result":"Nothing To Summarize"})
            
class SummarizePDF(Resource):
    def post(self):
        try:
            file=request.files['data_file']
            filename=file.filename
            if '.pdf' in filename:
                file.save("static/uploads/data.pdf")
                doc = fitz.open('static/uploads/data.pdf')
                article_text = ""
                for page in doc:
                    article_text+=page.get_text()
                jsonbody={"text":article_text}
                res=requests.post('http://localhost/summarize',json=jsonbody)
                responseObj=json.loads(res.text)
                summary=responseObj["result"]
                if res.status_code==200:
                    if responseObj["status"]==200:
                        return jsonify({"status":200,"result":summary})
                    else:
                        return jsonify({"status":400,"result":summary})
                else:
                    return jsonify({"status":res.status_code,"result":summary})
                    
            else:
                raise Exception()
        except Exception:
            return jsonify({"status":400,"result":"Nothing To Summarize"})

class SummarizeText(Resource):
    def post(self):
        data=request.get_json()
        text=data['copied-text']
        jsonbody={"text":text}
        res=requests.post('http://localhost/summarize',json=jsonbody)
        responseObj=json.loads(res.text)
        summary=responseObj["result"]
        if res.status_code == 200:
            if responseObj["status"]==200:
                return jsonify({"status":200,"result":summary})
            else:
                return jsonify({"status":400,"result":summary})
        else:
            return jsonify({"status":res.status_code,"result":summary})
    
class SummarizeWeb(Resource):
    def post(self):
        try:
            data=request.get_json()
            link=data['link']
            scraped_data = urllib.request.urlopen(link)
            article = scraped_data.read()
            parsed_article = bs.BeautifulSoup(article,'html.parser')
            paragraphs = parsed_article.find_all('p')
            text = ""
            for p in paragraphs:
                text += p.text
            jsonbody={"text":text}
            res=requests.post('http://localhost/summarize',json=jsonbody)
            responseObj=json.loads(res.text)
            summary=responseObj["result"]
            if res.status_code == 200:
                if responseObj["status"]==200:
                    return jsonify({"status":200,"result":summary})
                else:
                    return jsonify({"status":400,"result":summary})
            else:
                return jsonify({"status":res.status_code,"result":summary})
        except HTTPError:
            return jsonify({"status":403,"result":""})

class CalculateCosineSimilarityScore(Resource):
    def post(self):
        try:
            data=request.get_json()
            doc1=data['doc1']
            doc2=data['doc2']
            doc1_tokens=word_tokenize(doc1)
            doc2_tokens=word_tokenize(doc2)
            sw = stopwords.words('english')
            l1 =[];l2 =[]
            X_set = {w for w in doc1_tokens if not w in sw}
            Y_set = {w for w in doc2_tokens if not w in sw}
            # form a set containing keywords of both strings
            rvector = X_set.union(Y_set)
            for w in rvector:
                if w in X_set: l1.append(1) # create a vector
                else: l1.append(0)
                if w in Y_set: l2.append(1)
                else: l2.append(0)
            c = 0

            # cosine formula
            for i in range(len(rvector)):
                    c+= l1[i]*l2[i]
            cosine_score = c / float((sum(l1)*sum(l2))**0.5)
            return jsonify({"status":200,"score":cosine_score})
        except Exception as e:
            print(e)
            return jsonify({"status":400,"score":0})
            
        
@app.route("/", methods=['GET'])
def index():
    text="return render_template('summarize/home.html')"
    return render_template('base.html')
    
@app.route('/login',methods=['GET','POST'])
def login():
    return render_template('login/home.html')

@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('register/home.html')
    
@app.route('/summarize',methods=['GET'])
def summarize():
    return render_template('summarize/home.html')

@app.route('/similarity',methods=['GET'])
def similarity():
    return render_template('similarity/home.html')
    
api.add_resource(Summarizer,'/summarize')
api.add_resource(SummarizePDF,'/summarize/pdf')
api.add_resource(SummarizeText,'/summarize/text')
api.add_resource(SummarizeWeb,'/summarize/web')
api.add_resource(CalculateCosineSimilarityScore,'/similarity/cosine/calculate')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)