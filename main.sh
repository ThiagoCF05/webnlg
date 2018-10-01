# path to the project
PROJECT_PATH=/home/tcastrof/webnlg/WebNLG
# path to the machine translation system, which can be downloaded at http://data.statmt.org/wmt17_systems/
MT_PATH=/home/tcastrof/webnlg/wmt17_systems/en-de

TMP_PATH=/home/tcastrof/webnlg/tmp/
mkdir TMP_PATH

# PREPROCESSING
cd $PROJECT_PATH
python preprocess.py

# TRANSLATING
cd $MT_PATH
echo 'Translating  dev templates...'
./translate-reranked.sh < $TMP_PATH/temp.dev.en > $TMP_PATH/temp.dev.de

echo 'Translating dev texts...'
./translate-reranked.sh < $TMP_PATH/text.dev.en > $TMP_PATH/text.dev.de

echo 'Translating  train templates...'
./translate-reranked.sh < $TMP_PATH/temp.train.en > $TMP_PATH/temp.train.de

echo 'Translating train texts...'
./translate-reranked.sh < $TMP_PATH/text.train.en > $TMP_PATH/text.train.de

# POSTPROCESSING
cd $PROJECT_PATH
python postprocess.py