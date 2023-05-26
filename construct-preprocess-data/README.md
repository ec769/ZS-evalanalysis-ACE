This is the repository for the paper: Evaluating Zero-Shot Event Structures: Recommendations for Automatic Content Extraction (ACE) Annotations.

We adapted much of Wadden et al's pre-processing; thanks a lot to the authors.

The repository contains code for the full analyses in the paper (provided the same pre-processing).

To run the code, set up a virtualenv that uses an old version of Spacy.


```shell
conda deactivate
conda create --name ace-event-preprocess python=3.7
conda activate ace-event-preprocess
pip install -r scripts/data/ace-event/requirements.txt
pip install nltk
python -m spacy download en_core_web_sm
```

Then, collect the relevant files from the ACE data distribution with
```
bash ./construct-preprocess-data/scripts/data/ace-event/collect_ace_event.sh [path-to-ACE-data].
```
The results will go in `./construct-preprocess-data/data/ace-event/raw-data`.

To replicate analysis and use code for recommendation 1, run the following command: (If you want to consider pronouns as arguments, add the '--include_pronouns' flag at the end.)

python ./construct-preprocess-data/scripts/data/ace-event/parse_ace_event_mod1.py [output-name]

To run analysis for recommendation 1, run the command: 

python ./challenge-exp/challenge-1-exp.py [output-name]



To replicate analysis and use code for recommendation 2, run the following command: (If you want to consider pronouns as arguments, add the '--include_pronouns' flag at the end.)

python ./construct-preprocess-data/scripts/data/ace-event/parse_ace_event_mod2.py [output-name]

To run analysis for recommendation 2, run the command: 

python ./challenge-exp/challenge-2-exp.py [output-name]


Most of the code from the steps until running ...parse_ace_event_mod[1/2].py come from Wadden et al's pre-processing; we modify ...parse_ace_event_mod[1/2].py and share challenge-1-exp.py and challenge-2-exp.py. 
