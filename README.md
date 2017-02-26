# here the leafsighaway

This is the code used to generate the parts for *here, the leafsighaway*,
a mutable music-poem for instrumentalists, speakers, and audience.
The premiere performance and recording occured on November 21st, 2015,
and can be heard [here](https://www.youtube.com/watch?v=Ag-gPrtWQHo).
It is intended that with each performance of the piece, a completely new
set of parts be generated with this program.

## Setup

Both Python 3 and GNU lilypond must be installed and on your system path.

* Python 3 - https://www.python.org/ (be sure to install Python **3**)
* GNU Lilypond - http://lilypond.org/

Once these are installed, download or clone this repository.
From your system terminal (what's that? [Windows](http://www.wikihow.com/Open-the-Command-Prompt-in-Windows)
[Mac](http://www.wikihow.com/Open-a-Terminal-Window-in-Mac)), 
install the part maker package and its dependencies using pip:

```bash
cd here_the_leafsighaway
pip install -e .
```

To launch the program, run the main script with python:

```bash
python make_parts.py
```

You will be prompted to enter which parts (and how many of each) to generate,
as well as an approximate page count for the parts.

### Disclaimer...

Although it mostly works, the code in this repository is largely hackish spaghetti
cobbled together by a person writing their first nontrivial program. I've done
some minimal work to make it slightly more comprehensible, but for the most part
it has been left in its original form. My sincerest apologies to anyone trying to grok or
modify this mess...