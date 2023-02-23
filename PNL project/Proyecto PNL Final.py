# prototipo 
import pandas as pd
import numpy as np
import tensorflow
import tflearn
import nltk
from nltk.stem.lancaster import LancasterStemmer



def filtro_de_columnas(sentimiento,tema):
    filtro = df[(df["Sentimiento"]==sentimiento)&(df["Tema"]==tema)]
    filtro = filtro.iloc[:,0]
    
    return filtro

def preparacion_de_datos(data):
    palabras=[]
    etiquetas=[]
    docs_x=[]
    docs_y=[]

    for i in data["data"]:

        for x in i["Resumen"]:
            wrds = nltk.word_tokenize(x)
            palabras.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(i["Etiqueta"])

            if i["Etiqueta"] not in etiquetas:
                etiquetas.append(i["Etiqueta"])

    palabras =[stemmer.stem(w.lower()) for w in palabras if w != "?"]
    palabras =sorted(list(set(palabras)))      
    etiquetas =sorted(etiquetas)
    training =[]
    output =[]
    out_empty =[0 for _ in range (len(etiquetas))]
      
    for x, doc in enumerate(docs_x):
        bolsa = []
        wrds = [stemmer.stem(w.lower()) for w in doc]
        for w in palabras:
            if w in wrds:                    
                bolsa.append(1)
            else:
                bolsa.append(0)

            output_row =out_empty[:]
            output_row[etiquetas.index(docs_y[x])] = 1
            training.append(bolsa)
            output.append(output_row)
                
    training =np.array(training) 
    output =np.array(output) 

    return palabras,etiquetas,training,output

def bolsa_de_palabras(texto,palabras):
    bolsa=[0 for _ in range (len(palabras))]  
    palabras_s=nltk.word_tokenize(texto)
    palabras_n=[stemmer.stem(p.lower()) for p in palabras_s]

    for se in palabras_n:

        for i, w in enumerate(palabras):

            if w == se:
                bolsa[i]=1

    return np.array(bolsa)
    
def Respuesta(df,palabras,etiquetas):
    res = []

    for x in df["Resumen"]:
        result = model.predict([bolsa_de_palabras(x,palabras)])
        result_index = np.argmax(result)
        etiqueta = etiquetas[result_index]

        for eq in data["data"]:

            if eq['Etiqueta'] == etiqueta:
                respuesta = eq["Resultado"]

        res.append(respuesta)
        
    return res

def precision_test(testx,testy):
    cantidad=0
    asertividad=0

    for i,x in enumerate(testx):
        result = model.predict([bolsa_de_palabras(x,palabras)])
        result_index=np.argmax(result)
        etiqueta=etiquetas[result_index]

        for eq in data["data"]:

            if eq['Etiqueta'] == etiqueta:
                responses=eq["Resultado"]
        y=testy.iloc[[i]]
        if y["Tema"][i]==responses[0] and y["Sentimiento"][i]==responses[1] :
            cantidad=cantidad+1
            asertividad=asertividad+1       
        else:
            cantidad=cantidad+1

    return print("precision =",(asertividad*100)/cantidad,"%")

def creador_de_excel(df,palabras,etiquetas):
    r = Respuesta(df,palabras,etiquetas)
    c = 0
    
    for e in r:
        df2["Sentimiento"][c] = str(e[1])
        df2["Tema"][c] = str(e[0])
        c = c+1

    df2.to_excel("Result.xlsx",index=False)

def red(training,output):
    tensorflow.compat.v1.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,8)
    net = tflearn.fully_connected(net,len(output[0]),activation="softmax")
    net = tflearn.regression(net)
    model = tflearn.DNN(net)

    model.fit(training, output, n_epoch=5, batch_size=12, show_metric=True)

    model.save("model.tflearn")
    return model


stemmer = LancasterStemmer()

df = pd.read_excel('tranning PNL.xlsx')

df = df.dropna()

df = pd.DataFrame(df)

# agregar temas a filtrar ejem:filtro = ['desarrollo e innovación','Otros'] o dejar lista en blanco para no filtrar ejem:filtro = []
filtro = []

if bool(filtro): 
    df = df[df.Tema.isin(filtro)]

sentimientos = np.unique(df["Sentimiento"])
temas = np.unique(df["Tema"])
segmentos = []
divisor = 0

for x in sentimientos:

    for y in temas:
        segmentos.append([])  
        segmentos[divisor].append(y)
        segmentos[divisor].append(x)
        divisor=divisor+1

data = {"data":[]}

for x in segmentos:
    columna = filtro_de_columnas(x[1],x[0])

    if columna.empty == False:
        data["data"].append({"Etiqueta":[x[0]+" - "+x[1]],"Resumen":columna.tolist(),"Resultado":[x[0],x[1]]})

data = pd.DataFrame(data)

palabras,etiquetas,training,output = preparacion_de_datos(data)

model=red(training,output)

df2 = pd.read_excel('test PNL.xlsx')

df2 = df2.dropna()

df2 = pd.DataFrame(df2)

test_x=df2.iloc[:,0].to_list()
test_y=df2.iloc[:,1:]

precision_test(test_x,test_y)

creador_de_excel(df,palabras,etiquetas)

df2

