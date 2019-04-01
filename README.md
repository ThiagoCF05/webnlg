# Webnlg
The enriched version of the WebNLG dataset, described at [the INLG 2018 paper](https://aclweb.org/anthology/W18-6521).

### Description

WebNLG is a valuable resource and benchmark for the Natural Language Generation (NLG) community. However, as other NLG benchmarks, it only consists of a collection of parallel raw representations and their
corresponding textual realizations. This work aimed to provide intermediate representations of the data for the development and evaluation of popular tasks in the NLG pipeline architecture (Reiter and Dale, 2000), such as Discourse Ordering, Lexicalization, Aggregation and Referring Expression Generation.

### Last Version

The last version of the corpus (v1.3), available [here](https://github.com/ThiagoCF05/webnlg/tree/master/final), counts now with the annotation of the test part of the data. Here is the changes per version:

1. **v1.0**: first version with annotation of the train and development parts of the corpus and German translation.
2. **v1.1**: fix on some annotation mistakes. See Issue [#1](https://github.com/ThiagoCF05/webnlg/issues/1). (November 21st, 2018)
3. **v1.2**: annotation of the test part of the corpus. See Issue [#2](https://github.com/ThiagoCF05/webnlg/issues/2). (January 31st, 2019)
4. **v1.3**: tokenization by [NLTK](https://www.nltk.org/), leading to a better extraction of references and discourse ordering information. (January 31st, 2019)
5. **v1.4**: full revision of the delexicalized templates. (April 1st, 2019)

### German translation

Besides the official English version of the data (``en``), we also provide a silver-standard version of the corpus in German (``de``). The details on how to obtain the translation is presented on the following section and on the INLG 2018 paper.

### Scripts

To obtain the enriched version of the dataset as available in the mentioned directory, 
make sure to proper set up *the University of Edinburgh's Neural MT System for WMT17*, publicly available [here](http://data.statmt.org/wmt17_systems).  
After the settings, update the path variable ``MT_PATH`` in the ``main.sh`` script before execute it:

``
sh main.sh
``

### License

The WebNLG data is licensed under the following license: [CC Attribution-Noncommercial-Share Alike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/). The original version of the dataset may be found at [the official website of the WebNLG challenge](http://webnlg.loria.fr/pages/challenge.html).

### Citations:

```Tex
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
```

```Tex
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
```

```Tex
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
```
