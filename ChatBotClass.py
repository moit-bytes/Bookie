from abc import ABCMeta, abstractmethod
import requests

import re
import pandas as pd
import tensorflow_hub as hub
import tensorflow as tf
import tensorflow_text


import faiss, os

from tqdm import tqdm
from sklearn.neighbors import KNeighborsClassifier as knn
import numpy as np
import transformers
from transformers import pipeline
import ast, json
from sklearn.metrics.pairwise import cosine_similarity

class TFEncoder(metaclass=ABCMeta):
    """Base encoder to be used for all encoders."""
    def __init__(self, model_path:str):
        self.model = hub.load(model_path)
    
    @abstractmethod
    def encode(self, text:list):
        """Encodes text.
        Text: should be a list of strings to encode
        """
        
class USE(TFEncoder):
    """Universal sentence encoder"""
    def __init__(self, model_path):
        super().__init__(model_path)
        
    def encode(self, text):
        return self.model(text).numpy()
    
class USEQA(TFEncoder):
    """Universal sentence encoder trained on Question Answer pairs"""
    def __init__(self, model_path):
        super().__init__(model_path)
        
    def encode(self, text):
        return self.model.signatures['question_encoder'](tf.constant(s))['outputs'].numpy()
    
class BERT():
    """BERT models"""
    def __init__(self, model_name, layers="-2", pooling_operation="mean"):
        self.embeddings = BertEmbeddings(model_name, 
                                         layers=layers,
                                         pooling_operation=pooling_operation)

        self.document_embeddings = DocumentPoolEmbeddings([self.embeddings], fine_tune_mode='nonlinear')
        
    def encode(self, text):
        sentence = Sentence(text)
        self.document_embeddings.embed(sentence)
        return sentence.embedding.detach().numpy().reshape(1, -1)


# model_path = 'https://tfhub.dev/google/universal-sentence-encoder-qa/3'
# model_path = '../../models/universal-sentence-encoder-qa3/'

# https://arxiv.org/pdf/1803.11175.pdf
# model_path = '../../models/universal-sentence-encoder-large5/' #best for english

model_path = "https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3"
# model_path = '../../models/universal-sentence-encoder-multilingual-large3/'

# encoder = BERT('bert-base-uncased')


class FAISS:
    def __init__(self, dimensions:int):
        self.dimensions = dimensions
        self.index = faiss.IndexFlatL2(dimensions)
        self.snips = {}
        self.snip_id = 0

    
    def add(self, text:str, v:list, text_details:tuple):
        self.index.add(v)
        snip_details = (text,)+text_details
        print(snip_details)
        self.snips[self.snip_id] = snip_details
        self.snip_id += 1
        
    def search(self, v:list, k:int=10):
        distance, item_index = self.index.search(v, k)
        results = []
        for dist, i in zip(distance[0], item_index[0]):
            if i==-1:
                break
            else:
              results.append(self.snips[i][:-1]+(dist,)) 
                #print(f'{self.snips[i][0]}, %.2f'%dist)
        return results

    def __get_snip_id(self, v):
      try:
        ind = [k for k, vl in self.vectors.items() if v==vl[0]][0]
        return ind
      except:
        return -1

class VideoSemanticSearch(FAISS):
  def __init__(self, semantic_outlier_radius):
    self.encoder = USE(model_path)
    self.d = self.encoder.encode(['hello']).shape[-1]
    super().__init__(self.d)
    self.semantic_outlier_radius = semantic_outlier_radius

  def add(self, url, handle, v):
    self.index.add(v)
    snip_details = (url, handle, v)
    self.snips[self.snip_id] = snip_details
    self.snip_id += 1
  
  def add_pool(self, filepaths=[]):
    
    def isEnglish(s):
      try:
          s.encode(encoding='utf-8').decode('ascii')
      except UnicodeDecodeError:
          return False
      else:
          return True
      
    for path in filepaths:
      df = pd.read_csv(path)
      handles = df['Video Name'].values
      for handle, url in df[['Video Name', 'Video URL']].values:
        if type(handle) != float and type(url) != float:
          refined_handle = re.sub("bajaj|finserv", "", re.sub("([0-9\W]*)(?!\w)", "",  re.sub("\|.*", "", handle.lower()))).strip()
          if isEnglish(refined_handle):
            emb = self.encoder.encode(refined_handle)
            self.add(url, refined_handle, emb)

    """for doc_id, path in tqdm(enumerate(filepaths)):
      try:
        kwts = json.loads(open(path).read())

        for q in kwts['results']:
            text = q['text']
            emb = self.encoder.encode(text)
            self.add(text, emb, doc_id, q['timestamps'])

      except:
    
        trts = open(path).readlines()
        for st in trts:
          q = ast.literal_eval(st)
          text = q['text']
          emb = self.encoder.encode(text)
          self.add(text, emb, doc_id, [{"start":q["start"], "end":q["start"]+q["duration"]}])"""

    return 1


  def search_snip(self, s, k=10):
      emb = self.encoder.encode(s)
      res = self.search(emb, k)
      res = [r for r in res if r[-1]<=self.semantic_outlier_radius]
      if len(res) == 0:
        return [("Sorry no appropriate response could solve your query try framing a different query", 1e+7)]
      return res


class StaticQuerySearch(FAISS):
  def __init__(self, semantic_outlier_radius):
    self.encoder = USE(model_path)
    self.d = self.encoder.encode(['hello']).shape[-1]
    super().__init__(self.d)
    self.semantic_outlier_radius = semantic_outlier_radius
    
  def add(self, v, response):
    self.index.add(v)
    snip_details = (response,v)
    self.snips[self.snip_id] = snip_details
    self.snip_id += 1
  
  def add_pool(self, filepaths=[]):
    
    dfs = [pd.read_csv(path) for path in filepaths]
    for df in tqdm(dfs):
      for rowd in df.values:
        if type(rowd[0]) != float and type(rowd[1]) != float:
          text, response = rowd[0].replace("?", ""), rowd[1]#, rowd[3] 
          emb = self.encoder.encode(text)
          self.add(emb, response)
    return 1
  
  def search_snip(self, s, k=10):

      emb = self.encoder.encode(s.replace("?", ""))
      res = self.search(emb, k)
      res = [r for r in res if r[-1]<=self.semantic_outlier_radius]  #recommendations in radius of 100 euclideans
      if len(res) == 0:
        return [("Sorry no appropriate response could solve your query try framing a different query", 1e+7)]
      return res

class SmallTalkSearch(FAISS):
  def __init__(self, semantic_outlier_radius):
    self.encoder = USE(model_path)
    self.d = self.encoder.encode(['hello']).shape[-1]
    super().__init__(self.d)
    self.semantic_outlier_radius = semantic_outlier_radius
    
    
  def add(self, v, response,):
    self.index.add(v)
    snip_details = (response, v)
    self.snips[self.snip_id] = snip_details
    self.snip_id += 1
  
  def add_pool(self, ques=[]):
    
    for q in tqdm(ques):
        
        text = q.lower() 
        #res = self.conversor(transformers.Conversation(q.lower()), pad_token_id=50256)
        #res = str(res)
        #res = res[res.find("bot >> ")+6:].strip()
        emb = self.encoder.encode(text)
        self.add(emb, text)
    return 1
  
  def search_snip(self, s, k=10):

      emb = self.encoder.encode(s)
      res = self.search(emb, k)
      res = [r for r in res if r[-1]<=self.semantic_outlier_radius]  #recommendations in radius of 100 euclideans
      if len(res) == 0:
        return [("Sorry no appropriate response could solve your query try framing a different query", 1e+5)]
      return res





class ChatBot():
  def __init__(self):
    self.vsearch_engine = VideoSemanticSearch(1) #radius=1
    self.rsearch_engine = StaticQuerySearch(1) #radius=1
    self.stsearch_engine = SmallTalkSearch(10)
    self.vsearch_engine.add_pool(filepaths=["./Video_Final_DB.csv","./allianz_youtube.csv"]) #filepaths=['/content/keywords_timestamps.txt', '/content/transcript_timestamps.txt'])
    self.rsearch_engine.add_pool(filepaths=['./general_health_insurance_faqs.csv'])
    self.small_talk = ['Hi',
 'Hello',
 'How are you?',
 'What’s up?',
 'Yo',
 'How you doin?',
 'Good Morning',
 'Good Evening',
 'Good Afternoon',
 'Good Night',
 'What can you do?',
 'What can I do with you?',
 'What are you doing?',
 'Thanks',
 'Thank you',
 'Thanks dude',
 'Thanks lady',
 'My name is &lt;insert user name&gt;',
 'How can you help me?',
 'Help me please',
 'Talk to you later!',
 'Tell me something that you can do',
 'Say anything',
 'Will you marry me?',
 'Are you Single?',
 'Do you have a boyfriend',
 'girlfriend?',
 'Do you know other chatbots?',
 'Do you want to rule the world?',
 'Are you busy?',
 'Say something funny',
 'Can you say anything else',
 'What do you think of me?',
 'Happy &lt;insert holiday&gt;',
 'Do you love me?',
 'Can you fly?',
 'You are a genius!',
 'You are awesome',
 'great',
 'special',
 'Thanks so much!',
 'Thanks, that’s very helpful',
 'Yup, that’s true',
 'That’s accurate',
 'You are right',
 'Give me a fist bump',
 'I think you are great!',
 'Thumbs up',
 'You suck',
 'I hate you',
 'Go away',
 'That’s not right',
 'That’s not true',
 'That was stupid',
 'You are not helpful',
 'That was not the right answer',
 'Terrible',
 '&lt;expletive&gt;',
 'Which baseball',
 'football team do you like?',
 'You know nothing Jon Snow.',
 'Where’s Waldo?',
 'What’s the weather?',
 'Where’s the best restaurant in town?',
 'What should I eat today?',
 'Who is the best &lt;insert role&gt;?',
 'Who should I vote for?',
 'Who is the best digital assistant?',
 'Do you know Alexa?',
 'What’s your age?',
 'Can you sleep?',
 'Who is your boss?',
 'Who created you?',
 'Do you know other chatbots?',
 'What is your favorite color?',
 'Why did the chicken cross the road?',
 'Happy Birthday',
 'Do you know me?',
 'Are you my assistant?']
    self.stsearch_engine.add_pool(ques=self.small_talk)
    self.conversor = pipeline("conversational", model="microsoft/DialoGPT-medium")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    self.usr_database = {1:{"t_queries":[], "t+1_suggestions":[]}}

  
  import requests
  def search(self, name):
      url = "https://google-web-search.p.rapidapi.com/"

      querystring = {"query":name,"max":"1","site":"https://www.bajajallianz.com/"}

      headers = {
          "X-RapidAPI-Key": "00d6ea68d4msha77ac50f2364dd8p10dabfjsn21c29d49dc02",
          "X-RapidAPI-Host": "google-web-search.p.rapidapi.com"
      }

      response = requests.request("GET", url, headers=headers, params=querystring)
      res = response.json()
      final_des = res["results"][0]["description"].replace("\xa0..", "")
      url = res["results"][0]["url"]
      return final_des + f"refer this url for more details : {url}"

  
  def chat(self, usr_chat):

    def decider(source_distance, choices_distance, threshold_distance=5e-2):
      proximity_array = []
      for d in range(choices_distance.shape[0]):
        #if d == 2 and choices_distance[d] <=
        # self.rsearch_engine.semantic_outlier_radius
        # proximity_array.append(d)  #radius
        if abs(source_distance - choices_distance[d]) <= threshold_distance:
          proximity_array.append(d)
        else:
          pass
      return proximity_array
        
    try:
    #history = history or []
      usr_chat = usr_chat.lower()
      #if usr_chat in ["hello","hi", "hey", "good morning", "how are you"]:
      #  res = "Hello! You can ask me for all your basic queries"

      formal_text_resp = self.rsearch_engine.search_snip(usr_chat, 5)
      informal_text_resp = self.stsearch_engine.search_snip(usr_chat,1)[0]
      video_resp = self.vsearch_engine.search_snip(usr_chat, 5)

      formal_text_resp, recommend_formal_text_resp_next = formal_text_resp[0], formal_text_resp[1:]
      video_respf, recommend_video_resp_next = video_resp[0], video_resp[1:]
      
      informal_text_resp_text = self.conversor(transformers.Conversation(usr_chat), pad_token_id=50256)
      informal_text_resp_text = str(informal_text_resp_text)
      informal_text_resp_text = informal_text_resp_text[informal_text_resp_text.find("bot >> ")+6:].strip()

      
      total_dist = np.array([formal_text_resp[-1], informal_text_resp[-1], video_respf[-1]])
      
    
      
      total_resp_text = np.array([formal_text_resp[0], informal_text_resp_text, video_respf[0]])
      
      print(total_resp_text)
      #recommend_formal_text_resp_next = [t[0] for t in recommend_formal_text_resp_next]
      #recommend_video_resp_next = [t[0] for t in recommend_video_resp_next]
      #print(recommend_video_resp_next)
      #total_resp_text_recommended_next = np.array([recommend_formal_text_resp_next, recommend_video_resp_next])


      source_distance = np.min(total_dist)
      decided_categories = decider(source_distance, total_dist)

      #print(total_resp_text_recommended_next)
      #print(total_resp_text, decided_categories)
      if 1 in decided_categories:
        decided_categories = [1]
      else:
        pass
        #self.usr_database[1]["t+1_suggestions"] += total_resp_text_recommended_next[decided_categories].tolist()
        #self.usr_database[1]["t_queries"] += [usr_chat]

      if (0 in decided_categories) or (1 in decided_categories) :
        final_resp = {"yt_id":"", "flag":True, "text":"\n\n OR \n\n".join(total_resp_text[decided_categories].tolist())}
      else:
        ytid = re.findall("/watch\?v=(.*)&list", total_resp_text[2])[0]
        final_resp = {"yt_id":ytid, "flag":False, "text":""}
      if (1 in decided_categories):
        final_resp["text"] = self.search(usr_chat)

      return {"status": 1, "response":json.dumps(final_resp)}
    except Exception as e:
      print(e)
      return {"status" : 0, "response":"None"}
      #final_resp_text = "\n\n OR \n\n".join(total_resp_text[decided_categories].tolist())
      
      """
      if any([s in usr_chat for s in self.small_talk_ques]):
        res = self.informalchatter_engine()
      
        
      else:
        res1 = self.rsearch_engine.search_snip(usr_chat, 1)[0]
        res2 = self.vsearch_engine.search_snip(usr_chat, 1)[0]
        if abs(res2[-1] - res1[-1]) <=5e-2:
          res = res1[0] +  f"Pls have a look at our video solution for your query <video:{res2[0]}>"
        else:
          if res2[-1] < res1[-1]:
            res = f"Pls have a look at our video solution for your query <video:{res2[0]}>"
          else:
            res = res1[0]
        """

      #history += [(usr_chat, final_resp_text)]
      
    
  def recommend_chat_queries(self, usr):
    return self.usr_database[usr]["t+1_suggestions"]

                        
                        