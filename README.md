# Webnlg
The enriched version of the WebNLG dataset, described at the INLG 2018 paper.

The final version of the corpus is available at [``final``](https://github.com/ThiagoCF05/webnlg/tree/master/final), 
split in the English (``en``) and German (``de``) versions.

To obtain the enriched version of the dataset as available in the mentioned directory, 
make sure to proper set up *the University of Edinburgh's Neural MT System for WMT17*, publicly available [here](http://data.statmt.org/wmt17_systems).  
After the settings, update the path variable ``MT_PATH`` in the ``main.sh`` script before execute it:

``
sh main.sh
``

The WebNLG data is licensed under the following license: [CC Attribution-Noncommercial-Share Alike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/). The original version of the dataset may be found at [the official website of the WebNLG challenge](http://webnlg.loria.fr/pages/challenge.html).
