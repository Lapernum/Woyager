# Tree-Structure Two-Modes Music Recommendation
[Website demo](http://52.91.131.179)


![alt text](Images/TreeMusicRecommendation_structure_v1_white.png)
Installation
============
Voyager requires Python >=3.9 and Node.js >=16.13.0. We have tested on Ubuntu 20.04, Windows 11, and macOS.
You need to follow the instructions below to install Voyager.

Python Install
--------------
git clone https://github.com/MineDojo/Voyager
cd Voyager
pip install -e .

Node.js Install
---------------
In addition to the Python dependencies, you need to install the following Node.js packages:

cd voyager/env/mineflayer
npm install -g npx
npm install
cd mineflayer-collectblock
npx tsc
cd ..
npm install

Minecraft Instance Install
--------------------------
Voyager depends on Minecraft game. You need to install Minecraft game and set up a Minecraft instance.

Follow the instructions in Minecraft Login Tutorial to set up your Minecraft Instance.

Fabric Mods Install
-------------------
You need to install fabric mods to support all the features in Voyager. Remember to use the correct Fabric version
of all the mods.

Follow the instructions in Fabric Mods Install to install the mods.

Getting Started
===============
Voyager uses OpenAI's GPT-4 as the language model. You need to have an OpenAI API key to use Voyager. You
can get one from here.

After the installation process, you can run Voyager by:
