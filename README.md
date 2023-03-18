# NewsGPT: search Engine with GPT-4 Summarization and Keypoint extraction

Utilizing the GPT-4 understanding and reasoning features to develop a web search app that can 

(1) use either keyphrases or direct URL as inputs;

(2) send the search input to OpenAI GPT-4 API for inference;

(3) Using custom inference strategies: i.e. for News we want to extract key points and ideas we can learn from the author and design our custom questions and expect well-organized bulletpoint responses from GPT-4;

(4) Early feature testing with GPT-4 API (currently in limited beta).

Supported Python version: Python 3.8.16 ~ Python 3.10.10


Most important code and modifications in [defining view function for main webpage](https://github.com/jerryzhao173985/NewsGPT-search/blob/main/search/views.py).

If having trouble installing psycopg2 using pip: ```pip install psycopg2```

You should first do on Mac using brew install:

```brew install postgresql```

If having trouble connecting to the port and port not killed and wanted to open same port, do:

```lsof -n -i4TCP:8080```


```kill -9 PID```
