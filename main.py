# Program to measure the similarity between
# two sentences using cosine similarity.
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# X = input("Enter first string: ").lower()
# Y = input("Enter second string: ").lower()
X ="As a result, face recognition technology is best suited to marking the student's attendance without requiring any contact with any device. LITERATURE SURVEY As mentioned, the system's core is face recognition, which provides the most value to the system. OpenCV is used for image pre-processing and face detection, as well as face recognition on detected faces. And later the teacher has to do the extra work again of marking the attendance in an excel sheet or csv file or any attendance marking system. Fig10: Admin Window Fig11: Student Window After logging in with the necessary credentials, the student can mark his or her attendance using the window depicted in Figure 11. If the forgot password option is selected, display the forgot password screen and, after entering the details, email the user's credentials if the user exists on the system. If the user does not exist in the system, the model is trained, and a welcome email with the login credentials attached is sent to the user."
Y ="LITERATURE SURVEY As mentioned, the system's core is face recognition, which provides the most value to the system. OpenCV is used for image pre-processing and face detection, as well as face recognition on detected faces. And later the teacher has to do the extra work again of marking the attendance in an excel sheet or csv file or any attendance marking system. Fig10: Admin Window Fig11: Student Window After logging in with the necessary credentials, the student can mark his or her attendance using the window depicted in Figure 11. If the forgot password option is selected, display the forgot password screen and, after entering the details, email the user's credentials if the user exists on the system. If the user does not exist in the system, the model is trained, and a welcome email with the login credentials attached is sent to the user."

# tokenization
doc1_tokens = word_tokenize(X)
doc2_tokens = word_tokenize(Y)

# sw contains the list of stopwords
sw = stopwords.words('english')
l1 =[];l2 =[]

# remove stop words from the string
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
cosine = c / float((sum(l1)*sum(l2))**0.5)
print("similarity: ", cosine)
