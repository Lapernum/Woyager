# Tree-Structure Two-Modes Music Recommendation
[Website demo](http://52.91.131.179)


![alt text](Images/TreeMusicRecommendation_structure_v1_white.png)
Installation
============
Voyager requires Python >=3.9 and please use pip install -r requirements.txt to download all the required packages.

Python Install
--------------
git clone https://github.com/MineDojo/Voyager need to change

cd TreeMusicRecommendation

pip install -r requirements.txt

Change the openai key in backend/user/utils.py to your openai api key.




Getting Started
===============
Two-Modes Music Recommendation uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You
can get one from <a href="https://platform.openai.com/api-keys">here</a>.

After the installation process, you need to change the openai key in backend/user/utils.py to your openai api key.
```python
from voyager import Voyager
