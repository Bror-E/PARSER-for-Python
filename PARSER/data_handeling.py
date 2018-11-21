import os
import sys
import secrets
import Stringdata as sd
import random


def get_paper_names(folder = None):
    if not folder:
        folder = data_folder_gabriel
    if os.path.isdir(folder):
        return [files for files in os.listdir(folder) if '.yaml' in files]
    else:
        print("Could not find path: \n " + str(folder))

def get_paper_data(path, paper_title):
    string_data = sd.read_stringdata(os.path.join(path, paper_title))
    return_dict = {}
    for category_name,string_list in string_data.stringcategories.items():
        return_dict[category_name] = [string_data.stringdict.get(a) for a in string_list]
    if return_dict.get('All'): return_dict.pop('All')
    return return_dict

def get_paper_categories(path, paper_title):
    string_data = sd.read_stringdata(os.path.join(path, paper_title))
    string_categories = string_data.stringcategories
    if string_categories.get('All'): string_categories.pop('All')
    return string_categories

def get_paper_strings(path, paper_title,selected_categories):
    string_data = sd.read_stringdata(os.path.join(path, paper_title))
    return_strings = {}
    for category in selected_categories:
        return_strings[category] = [string_data.stringdict.get(a) for a in string_data.stringcategories.get(category)]
    return return_strings

#Input_strings should be {'category':[strings]}
def generate_input_data(input_strings,number_of_items):
    string_data = []
    for category,strings in input_strings.items():
        string_data = string_data+strings

    training_data = ''
    for _ in range(0,number_of_items):
        training_data = training_data+secrets.choice(string_data)
    return training_data

#Takes a list of strings and makes a long string of "number of items" length. 
def generate_stimuli(input_strings,number_of_items,random_seed = None):

    training_data = ''
    if random_seed is None:
        random_seed = random.randrange(sys.maxsize)
    rnd = random.Random(random_seed)
    for _ in range(0,number_of_items):
        random_index = rnd.randrange(len(input_strings))
        #training_data = training_data+secrets.choice(input_strings)
        training_data = training_data+input_strings[random_index]
    return training_data

def get_paper_primitives(path, paper_title):
    string_data = sd.read_stringdata(os.path.join(path, paper_title))
    readingframe = string_data.readingframe
    all_cateogries = string_data.stringcategories
    all_paper_strings = get_paper_strings(path, paper_title,all_cateogries)
    all_strings = ''
    for string_set in all_paper_strings.values():
        all_strings+= ''.join(string_set)    
    primitives = []
    if readingframe > 1:
        for index in range(0,len(all_strings),readingframe):
            primitives.append(all_strings[index:index+readingframe])
        primitives = list(set(primitives))
        return primitives
    else: 
        primitives = list(set(all_strings))
        return primitives

def run(input_string):
    return PARSER.run(input_string)

