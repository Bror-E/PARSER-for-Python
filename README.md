# A python implementation of PARSER: A model for word segmentation.
For my master thesis I implemented a well known model cogntive model for word segmentation. 
The original model is described  by Pierre Perruchet and Annie Vinter in their paper "PARSER: A Model for Word Segmentation."[1]

Additions to the original model:
- A method for grammatical induction on the learnt vocabuarly.




### FOLDERS:
#### PARSER:
The PARSER folder contains three files.
1. Stringdata.py
| This scripts contains methods to extract the data from the string-sets in the DATA folder.
2. data_handeling.py
| Contains methods to use the data collected using the Stringdata.py script.
3. PARSER_class.py
| The PARSER model. Contains methods for training and testing the model.

#### DATA:
This folder contains a number of string-sets that I used for experimentation in my master thesis. These string-sets are collected from.

#### Notebooks:
1. PARSER experiments.ipynb
Contains a number of replicated animal experiments using the PARSER model.












[1] Perruchet, P., & Vinter, A. (1998). PARSER: A model for word segmentation. Journal of memory and language, 39(2), 246-263.
