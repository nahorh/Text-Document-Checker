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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from time import sleep

app=Flask(__name__)
api=Api(app)

def clear_uploads():
    for file in os.listdir("./static/uploads/"):
                print(file)
                if os.path.exists("./static/uploads/{}".format(file)):
                    os.remove("./static/uploads/{}".format(file))

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

# class CalculateCosineSimilarityScore1(Resource):
#     def post(self):
#         try:
#             data=request.get_json()
#             doc1=data['doc1']
#             doc2=data['doc2']
#             doc1_tokens=word_tokenize(doc1)
#             doc2_tokens=word_tokenize(doc2)
#             sw = stopwords.words('english')
#             l1 =[];l2 =[]
#             X_set = {w for w in doc1_tokens if not w in sw}
#             Y_set = {w for w in doc2_tokens if not w in sw}
#             # form a set containing keywords of both strings
#             rvector = X_set.union(Y_set)
#             for w in rvector:
#                 if w in X_set: l1.append(1) # create a vector
#                 else: l1.append(0)
#                 if w in Y_set: l2.append(1)
#                 else: l2.append(0)
#             c = 0

#             # cosine formula
#             for i in range(len(rvector)):
#                     c+= l1[i]*l2[i]
#             cosine_score = c / float((sum(l1)*sum(l2))**0.5)
#             return jsonify({"status":200,"score":cosine_score})
#         except Exception as e:
#             print(e)
#             return jsonify({"status":400,"score":0})

class CalculateCosineSimilarityScore(Resource):
    def post(self):
        try:
            data=request.get_json()
            docs=data['docs']
            print(docs)
            names=data['names']
            vectorize = lambda Text: TfidfVectorizer().fit_transform(Text).toarray()
            similarity = lambda doc1, doc2: cosine_similarity([doc1, doc2])
            vectors=vectorize(docs)
            s_vectors=list(zip(names, vectors))
            plagiarism_results = set()
            for student_a, text_vector_a in s_vectors:
                new_vectors =s_vectors.copy()
                current_index = new_vectors.index((student_a, text_vector_a))
                del new_vectors[current_index]
                for student_b , text_vector_b in new_vectors:
                    sim_score = similarity(text_vector_a, text_vector_b)[0][1]
                    student_pair = sorted((student_a, student_b))
                    score = (student_pair[0], student_pair[1],sim_score)
                    plagiarism_results.add(score)
            plagiarism_results=list(plagiarism_results)
            plagiarism_results.sort()
            print(plagiarism_results)
            # return str(True)
            return jsonify({"status":200,"result":plagiarism_results})
        except Exception as e:
            print(e)
            # return e
            return str(False)

class SimilarityAPI(Resource):
    def post(self):
        try:
            # data=request.get_json()
            data_files=request.files
            names=list(data_files.keys())
            print('clearing files')
            clear_uploads()
            docs=[]
            print('saving files')
            for name in names:
                data_files[name].save(f'./static/uploads/{name}')
            print('reading pdf files')
            for file in os.listdir("./static/uploads/"):
                print(file)
                doc = fitz.open(f'./static/uploads/{file}')
                article_text = ""
                for page in doc:
                    article_text+=page.get_text()
                doc.close()
                print(article_text)
                print("----------------------------------------------------------------")
                if len(article_text)>0:
                    docs.append(article_text)
            json_body={"docs":docs,"names":list(names)}
            # for doc in docs:
            #     print(doc)
            #     print("----------------------------------------------------------------")
            res=requests.post("http://localhost/similarity/cosine/calculate",json=json_body)
            if res.status_code == 200:
                jsonObj=json.loads(res.text)
                print(jsonObj)
                clear_uploads()
                return jsonify({"result":jsonObj['result']})
            else:
                clear_uploads()
                return str(False)
        except Exception as e:
            clear_uploads()
            print(e)
            return str(False)
        
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
api.add_resource(SimilarityAPI,'/similarity')
api.add_resource(CalculateCosineSimilarityScore,'/similarity/cosine/calculate')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)