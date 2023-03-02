import pandas as pd
import re
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from nltk.stem.lancaster import LancasterStemmer 

def PNL(data):
    lts = LancasterStemmer()
    data = [x.split() for x in data]
    data = [[lts.stem(i.lower()) for i in x]for x in data]
    data = [' '.join(x) for x in data] 
    return data

def filtro(df):  
    df = df.drop(df[(df["Tema"]=='Reporte Parque CDS')].index)
    df = df.dropna()
    df = df.reset_index()

    df['Sentimiento'] = df['Sentimiento'].apply(lambda x: 'Neutral' if x == 'No sentiment' else x)
    data = df.copy() 

    data = preparacion_datos(data)
    
    with open("feelings.json",encoding='utf-8') as file:
        fe = json.load(file)

    data2 = pd.DataFrame(columns=df.columns)

    positivos = PNL(fe['sentimientos'][0]['Positivos'])
    negativos = PNL(fe['sentimientos'][1]['Negativos'])

    data['Resumen'] = PNL(data['Resumen'])

    for i,x in enumerate(data['Resumen']):
        pos = r'\b(' + '|'.join(positivos) + r')\b'
        neg = r'\b(' + '|'.join(negativos) + r')\b'

        if len(re.findall(pos, x.lower())) > len(re.findall(neg, x.lower())) and data['Sentimiento'][i]=='Positive':
            data2 = pd.concat([data2, data.loc[i].to_frame().T], ignore_index=True)

        elif len(re.findall(pos, x.lower())) < len(re.findall(neg, x.lower())) and data['Sentimiento'][i]=='Negative':
            data2 = pd.concat([data2, data.loc[i].to_frame().T], ignore_index=True)

        elif len(re.findall(pos, x.lower())) == len(re.findall(neg, x.lower())) and data['Sentimiento'][i]=='Neutral':
            data2 = pd.concat([data2, data.loc[i].to_frame().T], ignore_index=True)

    return data2.drop(columns=['index','level_0'])

def preparacion_datos(data):
    data['Resumen'] = data['Resumen'].apply(lambda x: x.lower()) 
    data['Resumen'] = data['Resumen'].str.replace('[^\w\s]','') 
    data = data.dropna()
    data = data.reset_index()
    return data

def salidas(data):
    salida = [str(x)+";"+str(y) for x,y in zip(data['Sentimiento'],data['Tema'])]
    return salida

def crear_excel(results,data):

    for i,x in enumerate(results):
        se,te = x.split(";")
        data["Sentimiento"][i] = str(se)
        data["Tema"][i] = str(te)

    data = data.drop(columns=['index'])

    print(data.head(3))
    data.to_excel('results.xlsx', index=False)


def precision(data,val_output):
    data = preparacion_datos(data)

    val_features = vectorizer.transform(data['Resumen'])
    accuracy = clf.score(val_features, val_output)
    return print("Exactitud del modelo:", accuracy)

df = pd.read_excel('Data Train.xlsx')

df2 = pd.read_excel('New Data.xlsx')
df2 = df2.dropna()
df2 = df2.reset_index()
test_data = df2.copy() 
 
df = filtro(df)

train_data = df.sample(frac=0.8, random_state=40)
val_data = df.drop(train_data.index)

test_data = preparacion_datos(test_data)

train_output = salidas(train_data)
val_output = salidas(val_data)

vectorizer = CountVectorizer()
vectorizer.fit(train_data['Resumen'])
train_features = vectorizer.transform(train_data['Resumen'])

clf = LogisticRegression(penalty = 'l2', solver = 'newton-cg',random_state = 42,max_iter = 500)

clf.fit(train_features, train_output)


test_features = vectorizer.transform(PNL(test_data['Resumen']))
results = clf.predict(test_features)

crear_excel(results,df2)

precision(val_data,val_output)


