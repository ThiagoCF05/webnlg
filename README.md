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

Citations:

``
@InProceedings{ferreiraetal2018,
  author = 	"Castro Ferreira, Thiago
		and Moussallem, Diego
		and Wubben, Sander
		and Krahmer, Emiel",
  title = 	"Enriching the WebNLG corpus",
  booktitle = 	"Proceedings of the 11th International Conference on Natural Language Generation",
  year = 	"2018",
  series = {INLG'18},
  publisher = 	"Association for Computational Linguistics",
  address = 	"Tilburg, The Netherlands",
}
``

``
@InProceedings{gardentetal017,
  author = 	"Gardent, Claire
		and Shimorina, Anastasia
		and Narayan, Shashi
		and Perez-Beltrachini, Laura",
  title = 	{Creating Training Corpora for {NLG} Micro-Planners},
  booktitle = 	"Proceedings of the 55th Annual Meeting of the Association for      Computational Linguistics (Volume 1: Long Papers)    ",
  series = {ACL'17},
  year = 	"2017",
  publisher = 	"Association for Computational Linguistics",
  pages = 	"179--188",
  address = 	"Vancouver, Canada",
  doi = 	"10.18653/v1/P17-1017",
  url = 	"http://www.aclweb.org/anthology/P17-1017"
}
``

``
@InProceedings{ferreiraetal2018b,
  author = 	"Castro Ferreira, Thiago
		and Moussallem, Diego
		and K{\'a}d{\'a}r, {\'A}kos
		and Wubben, Sander
		and Krahmer, Emiel",
  title = 	"NeuralREG: An end-to-end approach to referring expression generation",
  booktitle = 	"Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
  year = 	"2018",
  publisher = 	"Association for Computational Linguistics",
  pages = 	"1959--1969",
  location = 	"Melbourne, Australia",
  url = 	"http://aclweb.org/anthology/P18-1182"
}
``
