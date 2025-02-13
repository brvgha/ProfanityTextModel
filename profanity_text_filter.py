# -*- coding: utf-8 -*-
"""profanity_text_filter.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1gLRcdo-CSyRJwcHVUmxrzBv5oqQrvU0O
"""

import tensorflow as tf
import keras as k
import pandas as pd
import sklearn as sk
import random as r
import pickle
import math as m
import re
print(tf.__version__)
print(k.__version__)
print(pd.__version__)
print(sk.__version__)

with open('./drive/MyDrive/Project/ProfanityTextFilterModel/words.txt') as f:
  clean_words = f.read().splitlines()

clean_words = r.choices(clean_words, k=1500)
severity_level = [0.50 for _ in range(len(clean_words))]
clean_words = {"text" : clean_words, "severity_rating" : severity_level}
clean_words_df = pd.DataFrame(clean_words)
print(clean_words_df.head())
df = pd.read_csv('./drive/MyDrive/Project/ProfanityTextFilterModel/profanity_en.csv')
df = pd.concat([df,clean_words_df], ignore_index=True)
print(df.head())

profanity_en_df = pd.read_csv('./drive/MyDrive/Project/ProfanityTextFilterModel/profanity_en.csv')
offensive_lang_df = pd.read_csv('./drive/MyDrive/Project/ProfanityTextFilterModel/OffensiveLang.csv')
labeled_data_df = pd.read_csv('./drive/MyDrive/Project/ProfanityTextFilterModel/labeled_data.csv')

def remove_identifier(string: str):
  try:
    ind = string.find(":")
    return string[ind+1:len(string)]
  except:
    return string

def remove_amp_char(string: str):
  try:
    ind = string.find("&amp;")
    return string[0:ind]
  except:
    return string

def remove_quotes(string: str):
  try:
    ind = string.find("\"")
    return string[0:ind]
  except:
    return string

def convert_to_numeric_offense(word):
  if word == "Offensive":
    return 1
  return 0

def count_to_bool(num: int):
  if num > 0:
    return 1
  else:
    return 0

def clean_unknown_chars(word: str):
  word = re.sub(r'&.*?;', '', word)
  return word

def clean_mentions(word: str):
  word = re.sub(r'@.* ', '', word)
  return word

profanity_en_df["text"] = profanity_en_df["text"].str.lower()
profanity_en_df = profanity_en_df[["text", "severity_rating"]]
severity_to_bool = profanity_en_df["severity_rating"] > 1.4
profanity_en_df["severity_rating"] = severity_to_bool.astype(int)

offensive_lang_df["Final Annotation"]  = offensive_lang_df["Final Annotation"].apply(convert_to_numeric_offense)
offensive_lang_df["Text"] = offensive_lang_df["Text"].str.lower()
offensive_lang_df = offensive_lang_df[["Text", "Final Annotation"]]
offensive_lang_df = offensive_lang_df.rename(columns={"Text": "text", "Final Annotation": "severity_rating"})


hate_or_offensive = (labeled_data_df['hate_speech'] > 1) | (labeled_data_df['offensive_language'] > 1)
labeled_data_df = labeled_data_df[["tweet", "count"]]
labeled_data_df["count"] = hate_or_offensive.astype(int)
labeled_data_df["tweet"] = labeled_data_df["tweet"].apply(remove_identifier)
labeled_data_df["tweet"] = labeled_data_df["tweet"].apply(remove_amp_char)
labeled_data_df["tweet"] = labeled_data_df["tweet"].apply(remove_quotes)
labeled_data_df["tweet"] = labeled_data_df["tweet"].apply(clean_unknown_chars)
labeled_data_df["tweet"] = labeled_data_df["tweet"].apply(clean_mentions)
labeled_data_df = labeled_data_df.rename(columns={"tweet": "text", "count": "severity_rating"})
labeled_data_df["severity_rating"] = labeled_data_df["severity_rating"].apply(count_to_bool)

df = pd.concat([profanity_en_df, offensive_lang_df, labeled_data_df], ignore_index=True)
print(df.tail())

#df = df.drop(['canonical_form_1', 'canonical_form_2', 'canonical_form_3', 'category_1', 'category_2', 'category_3', 'severity_description'], axis=1)
#df["text"] = df["text"].str.lower()
#print(df.head())

tfidf = sk.feature_extraction.text.TfidfVectorizer(max_features=m.ceil(len(df)*0.525))
X = tfidf.fit_transform(df['text']).toarray()

X_train, X_test, y_train, y_test = sk.model_selection.train_test_split(X, df['severity_rating'], test_size=0.2, random_state=42)

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation = 'sigmoid') # this does probability (0 AND 1)
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mean_squared_error')

model.fit(X_train, y_train, epochs=10, batch_size=64, validation_split=0.2)

y_pred = model.predict(X_test)
loss = model.evaluate(X_test, y_test)
print("Loss:", loss)

model.predict(tfidf.transform(["where is my supersuit"]).toarray())

model.predict(tfidf.transform(["country roads take me home"]).toarray())

model.save('./drive/MyDrive/Project/ProfanityTextFilterModel/text_profanity_model.keras')
pickle.dump(tfidf, open('./drive/MyDrive/Project/ProfanityTextFilterModel/tfidf.pkl', 'wb'))

