# import pandas as pd
# import numpy as np
import json
import time
from bs4 import BeautifulSoup  # requires lxml
from email_reply_parser import EmailReplyParser

def profile():
    df = pd.DataFrame.from_csv('test.csv')
    ground = time.time()
    content = df.content.values[np.argmax([len(d) for d in df.content.values])]
    start = time.time()
    parser = EmailReplyParser(language='fr')
    print(str(time.time() - start) + 'init parser')
    start = time.time()
    res = parser.parse_reply(content)
    print(str(time.time() - start) + 'parse')
    start = time.time()
    soup = BeautifulSoup(res, 'lxml')
    text = soup.getText(' ')
    print(str(time.time() - start) + 'soup')
    print(f'Total time: {time.time() - ground}')

def verify():
    parser = EmailReplyParser(language='fi')
    texts = json.load(open('test/emails/emails.json'))
    texts = list(filter(lambda d: type(d) == str, texts))
    parsed = []
    for text in texts:
        # print(text)
        soup = BeautifulSoup(text, 'lxml')
        text = soup.getText('\n')
        print(text)
        text = parser.parse_reply(text)
        parsed.append(text)
        print(text)

if __name__ == '__main__':
    # profile()
    verify()
