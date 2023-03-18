from django.shortcuts import render
import requests
from bs4 import BeautifulSoup as bs
from newspaper import Article
import openai
import time
import re
# Enter the custom API key starting with "sk-"
openai.api_key = ""

def split_into_sentences(text):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"

    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    if "..." in text: text = text.replace("...","<prd><prd><prd>")
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

def is_valid_url(url):
    if url == "":
        return False
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)


def ask(question):
    tic = time.time()
    question += """

----------------------------------------

Can you tell me what can we learn from this article? What is the auther's key points and argument? Be as detailed as you can. 
"""
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": "You are GPT-4, a large language model trained by OpenAI. Answer as concisely as possible."},
                {"role": "user", "content": question}
        ]
    )
    toc = time.time()
    print(toc-tic, 'sec Elapsed')
    return (res['choices'][0]['message']['content'])
    
# Create your views here.
def index(request):
    return render(request, 'index.html')

def search(request):

    if request.method == 'POST':
        final_result = []
        search = request.POST['search']
        if is_valid_url(search):
            article = Article(search)
            article.download()
            article.parse()
            output = ask(article.text)
            sentences = split_into_sentences(output)

            final_result.append((sentences[0], search, output, sentences[-1]))
            context = {
                'final_result': final_result
            }

            return render(request, 'search.html', context)
        
        url = 'https://www.ask.com/web?q='+search
        res = requests.get(url)
        soup = bs(res.text, 'lxml')

        result_listings = soup.find_all('div', {'class': 'PartialSearchResults-item'})

        for result in result_listings[:2]:
            result_title = result.find(class_='PartialSearchResults-item-title').text
            result_url = result.find('a').get('href')
            
            # result_desc = result.find(class_='PartialSearchResults-item-abstract').text
            article = Article(result_url)
            article.download()
            article.parse()
            output = ask(article.text)
            sentences = split_into_sentences(output)
            if "1." in sentences[0]:
                result_desc = " ".join(sentences[:-1])
            else:
                result_desc = " ".join(sentences[1:-1])
            if result_desc[-1]=="." and result_desc[-2].isnumeric():
                result_desc += sentences[-1]

            final_result.append((result_title, result_url, result_desc, sentences[-1]))

        context = {
            'final_result': final_result
        }

        return render(request, 'search.html', context)

    else:
        return render(request, 'search.html')
