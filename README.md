# WebNLG
The enriched version of the WebNLG dataset, described at [the INLG 2018 paper](https://aclweb.org/anthology/W18-6521).

### Description

WebNLG is a valuable resource and benchmark for the Natural Language Generation (NLG) community. However, as other NLG benchmarks, it only consists of a collection of parallel raw representations and their
corresponding textual realizations. This work aimed to provide intermediate representations of the data for the development and evaluation of popular tasks in the NLG pipeline architecture (Reiter and Dale, 2000), such as Discourse Ordering, Lexicalization, Aggregation and Referring Expression Generation.

### Data

Here are the changes per version:

- [**v1.5**](data/v1.5): English Lexicalization templates, introduced in the EMNLP 2019 paper "Neural data-to-text generation: A comparison between pipeline and end-to-end architectures". (August 22th, 2019)
- [**v1.4**](data/v1.4): full revision of the delexicalized templates. (April 1st, 2019)
- [**v1.3**](data/v1.3): tokenization by [NLTK](https://www.nltk.org/), leading to a better extraction of references and discourse ordering information. (January 31st, 2019)
- [**v1.2**](data/v1.2): annotation of the test part of the corpus. See Issue [#2](https://github.com/ThiagoCF05/webnlg/issues/2). (January 31st, 2019)
- [**v1.1**](data/v1.1): fix on some annotation mistakes. See Issue [#1](https://github.com/ThiagoCF05/webnlg/issues/1). (November 21st, 2018)
- [**v1.0**](data/v1.0): first version with annotation of the train and development parts of the corpus and German translation.

**BETA**
- [**v2.0 (BETA)**](data/v2.0): Tree templates. (April 1st, 2019)

### Example

```xml
<entry category="Monument" eid="Id5" size="3">
    <originaltripleset>
        <otriple>11th_Mississippi_Infantry_Monument | region | Adams_County,_Pennsylvania</otriple>
        <otriple>11th_Mississippi_Infantry_Monument | established | 2000</otriple>
        <otriple>11th_Mississippi_Infantry_Monument | category | Contributing_property</otriple>
    </originaltripleset>
    <modifiedtripleset>
        <mtriple>11th_Mississippi_Infantry_Monument | location | Adams_County,_Pennsylvania</mtriple>
        <mtriple>11th_Mississippi_Infantry_Monument | established | 2000</mtriple>
        <mtriple>11th_Mississippi_Infantry_Monument | category | Contributing_property</mtriple>
    </modifiedtripleset>
    # lexical entry
    <lex comment="good" lid="Id1">
        # ordered tripleset segmented in sentences
        <sortedtripleset>
            <sentence ID="1">
                <striple>11th_Mississippi_Infantry_Monument | location | Adams_County,_Pennsylvania</striple>
            </sentence>
            <sentence ID="2">
                <striple>11th_Mississippi_Infantry_Monument | established | 2000</striple>
                <striple>11th_Mississippi_Infantry_Monument | category | Contributing_property</striple>
            </sentence>
        </sortedtripleset>
        # extracted referring expressions
        <references>
            <reference entity="11th_Mississippi_Infantry_Monument" number="1" tag="AGENT-1" type="description">The 11th Mississippi Infantry Monument</reference>
            <reference entity="Adams_County,_Pennsylvania" number="2" tag="PATIENT-1" type="name">Adams County , Pennsylvania</reference>
            <reference entity="11th_Mississippi_Infantry_Monument" number="3" tag="AGENT-1" type="pronoun">It</reference>
            <reference entity="2000" number="4" tag="PATIENT-2" type="name">2000</reference>
            <reference entity="Contributing_property" number="5" tag="PATIENT-3" type="name">contributing property</reference>
        </references>
        # original text
        <text>
            The 11th Mississippi Infantry Monument which is located in Adams County, Pennsylvania. It was established in 2000 and falls under the category of contributing property.
        </text>
        # text with delexicalized referring expressions
        <template>
            AGENT-1 which is located in PATIENT-1 . AGENT-1 was established in PATIENT-2 and falls under the category of PATIENT-3 .
        </template>
        # lexicalization template
        <lexicalization>
            AGENT-1 which VP[aspect=simple,tense=present,voice=active,person=3rd,number=singular] be located in PATIENT-1 . AGENT-1 VP[aspect=simple,tense=past,voice=passive,person=null,number=singular] establish in PATIENT-2 and VP[aspect=simple,tense=present,voice=active,person=3rd,number=null] fall under DT[form=defined] the category of PATIENT-3 .
        </lexicalization>
    </lex>
</entry>
```

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
