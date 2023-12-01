# Tree-Structure Two-Modes Music Recommendation
[Website demo](http://52.91.131.179)


![alt text](Images/TreeMusicRecommendation_structure_v1_white.png)
Installation
============
Voyager requires Python >=3.9 and please use pip install -r requirements.txt to download all the required packages.

Python Install
--------------
```
git clone https://github.com/MineDojo/Voyager need to change
cd TreeMusicRecommendation
pip install -r requirements.txt
```


Getting Started
===============
Two-Modes Music Recommendation uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You
can get one from <a href="https://platform.openai.com/api-keys">here</a>.

After the installation process, you need to change the openai key in **backend/user/utils.py** to your openai api key.
```python
** backend/user/utils.py **
def fetch_user_tag(top_artists):
    """
    Fetches the top three tags of the user based on the top artists preference of a user
    :param top_artists: list of artists
    :return: top three tags with each tag as a string
    """
    if not top_artists:
        return ""
    client = OpenAI(
        api_key="your own opeanai api key",
    )...
```
Now you can start to run the program.
For Unix/Linux/Mac:
```
export FLASK_APP=main.py
flask run
```
For Windows:
```
set FLASK_APP=main.py
flask run
```





