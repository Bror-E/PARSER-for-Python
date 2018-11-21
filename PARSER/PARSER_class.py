#This is a class based PARSER implementation. Where one class is one model. Makes things easier for direct input,output, storing of models etc etc. 
import random
import sys


class PARSER:

    def __init__(self,percept_shaper = None,parameters = None,primitives = None, random_seed = None):
        self.percept_shaper = percept_shaper
        self.parameters = parameters
        self.random_seed = random_seed
        self.primitives = primitives

    def set_percept_shaper(self, ps):
        #Is None, means to start over
        if ps is None:
            self._percept_shaper= dict()
        #If it is a dict, then it is a already initialized percept shaper
        elif type(ps) is dict:  
            self._percept_shaper = ps
        # If it is a list, it is a list of primitives, meaning it should be intitialized.
        elif type(ps) is list:
            self._percept_shaper = {primitive:1 for primitive in ps}    #OBS:Could get new_unit_weight.
    
    def get_percept_shaper(self):
        return self._percept_shaper
    
    def set_parameters(self, parameters):
        self._parameters = PARSER.get_default_parameters()
        if parameters is not None:
            for name,value in parameters.items():
                if name == 'random_seed':
                    self._random_seed = value
                else:
                    self._parameters[name] = value
    
    def get_parameters(self):
        return self._parameters

    def set_random_seed(self,seed):
        if seed is None:
            seed = random.randrange(sys.maxsize)
        self.random = seed
        self._random_seed = seed

    def get_random_seed(self):
        return self._random_seed

    def set_random(self,seed):
        self._random = random.Random(seed)
        self.parameters['random_seed'] = seed

    def get_random(self):
        return self._random

    def set_primitives(self,prim):
        if prim is None:
            self._primitives = []
        else:
            self._primitives = list(prim)
    def get_primitives(self):
        return self._primitives

    def run_til_end(self, input_string,primitives=None, print_progress =None):
        
        if print_progress:
            length = len(input_string)
            #int(((length-len(input_string))/length)*100)
            progress = int(((length-len(input_string))/length)*100)
            print(str(progress)+ "%, [" + str(length-len(input_string))+ "/" +str(length)+"]")
            while input_string:
                input_string = self.run(input_string, primitives)
                if progress != int(((length-len(input_string))/length)*100):
                    print(str(progress)+ "%, [" + str(length-len(input_string))+ "/" +str(length)+"]")
                    progress = int(((length-len(input_string))/length)*100)

        else:
            while input_string:
                input_string = self.run(input_string, primitives)
        return input_string

    def run(self, input_string, primitives = None):
        #initialize all of the model parts
        if self.primitives is None or self.primitives == []: 
            self.primitives = PARSER.initialize_primitives(input_string,primitives)
        if not self.percept_shaper or self.percept_shaper is None: 
           #print("Setting up ps")            
            self.percept_shaper = self.primitives
            #print(self.percept_shaper)
        #This is the actuall running of the model:
        size_of_next_percept = self.random.randint(self.parameters['min_percept_size'],self.parameters['max_percept_size'])
        perceived_units,input_string = self.percieve(size_of_next_percept, input_string)
        new_percept = ''.join(perceived_units)
        #To stay consisten with Figure 1 of the PARSER paper, we include the if here. 
        # Adds weight to the unit or 
        #print(new_percept)
        if perceived_units:
            if new_percept in self.percept_shaper:
                if self.percept_shaper[new_percept] >= self.parameters['shaping_threshold']:
                    self.percept_shaper[new_percept] += self.parameters['add_shaped_weight']
            else:
                self.percept_shaper[new_percept] = self.parameters['new_unit_weight']
            # If the number of percieve unites are longer than one, then add weight to its components. 
            if len(perceived_units) > 1: 
                for unit in perceived_units:
                    self.percept_shaper[unit] += self.parameters['add_shaped_weight']
            self.interference(perceived_units)
            self.forget(new_percept)
        #print(self.percept_shaper)
        return input_string
        #print(perceived_units, self.percept_shaper)
        
    def percieve(self, number_of_units, input_string):
        percepts_over_threshold = [percept for percept,weight in self.percept_shaper.items() if weight >= self.parameters['shaping_threshold']]
        max_length = max(map(len,percepts_over_threshold))
        percieved_units = []
        for i in range(number_of_units):
            #If the length of the longst percept is longer than the length of the input string
            if max_length > len(input_string):  
                max_length = len(input_string)
            #if the max length is 0 means that the input string is empty and we return what we have
            if max_length == 0:
                return percieved_units, input_string
            possible_unit = input_string[:max_length]
            while possible_unit not in percepts_over_threshold and len(possible_unit)>1:
                if possible_unit in self.primitives:
                    percieved_units.append(possible_unit)
                    break
                else:
                    possible_unit = possible_unit[:-1]
            input_string = input_string[len(possible_unit):]
            if possible_unit != "":
                percieved_units.append(possible_unit)
        return percieved_units, input_string

    def interference(self, percieved_units):
        # Filters the list of percieved units for units that are not part of the primitives. 
        perceived_units_not_primitives = [unit for unit in percieved_units if unit not in self.primitives]
        # Splits all of the the units from the list above into its basic pieces. This results in a list of lists
        list_of_splits = [self.split_unit(unit) for unit in perceived_units_not_primitives]
        # Interfernce points = the flat version of the lists_of_splits list. Example of interfernce points = ['a','c','ac']
        interference_points = [elem for sublist in list_of_splits for elem in sublist]
        # For each of the points in the interfercene points.
        for point in interference_points:
            if point in self.percept_shaper:    #If the point is in memory, then interfer with uit.
                self.percept_shaper[point] += self.parameters['interference_weight']

    def get_all_possible_paths(string_set,primitives):
        string_set_no_primitives = [unit for unit in string_set if unit not in primitives]
        list_of_paths = [PARSER.split_unit_open(unit,primitives) for unit in string_set_no_primitives]
        return list_of_paths

    def forget(self,newly_perceieved_unit):
        for percept,weight in list(self.percept_shaper.items()):
            if weight <=0 and percept not in self.primitives:
                del self.percept_shaper[percept]
            elif percept == newly_perceieved_unit:
                continue
            else:
                #print("Forgetting",percept)
                self.percept_shaper[percept] += self.parameters['forgetting_weight']
    
    def test_explicit(self,test_input, print_output = False):
        if isinstance(test_input,str):
            if test_input in self.percept_shaper:
                if self.percept_shaper[test_input] >= self.parameters['shaping_threshold']:
                    if print_output: 
                        print(test_input, "\t is CONSISTENT.")
                    return True
            else:
                if print_output: 
                    print(test_input, "\t is VIOLATING:")
                return False

        elif isinstance(test_input,list):
            #number_of_consistent = [test_string for test_string in test_input if test_string in self.percept_shaper]
            return sum([1 for test_string in test_input if self.test_explicit(test_string,print_output)])
        
        elif isinstance(test_input,dict):
            return {category:self.test_explicit(strings,print_output) for category,strings in test_input.items()}

    # Is automatically set to return the number of correctly identified grammar consistent strings.
    def test_implicit(self,test_input,print_output =False, detect_violation = False,get_failed = False):
        if isinstance(test_input,str):
             return self.single_test_string(test_input,print_output, detect_violation = detect_violation, get_failed = get_failed)

        elif isinstance(test_input,list):
            number_of_consistent = sum([1 for test_string in test_input if self.single_test_string(test_string, print_output,detect_violation=detect_violation)])
            return number_of_consistent
        
        elif isinstance(test_input,dict):
            return {category:self.test(strings) for category,strings in test_input.items()}

    def single_test_string(self, test_string,print_output = False,detect_violation = False,get_failed = False):
        no_primitives_over_threshold = [percept for percept,weight in self.percept_shaper.items() if weight >=1 and percept not in self.primitives]        
        #Split in to smaller parts
        list_of_splits = [self.split_unit(percept) for percept in no_primitives_over_threshold]
        #Filter out the primitives from the list, as they cannot be used to make combinations/edges
        possible_matches = list(set([elem for sublist in list_of_splits for elem in sublist if elem not in self.primitives]))
        completed, failed, matches = self.build_from_substrings(possible_matches,test_string)
        if completed == test_string:
            if print_output: print(test_string, "\t is CONSISTENT:", completed)
            if get_failed:
                return (not detect_violation, completed, failed)
            return not detect_violation
            #print("possible build")
            #for substring,list_of_matches in matches.items():
             #   print("Built '"+substring+"' from: "+min(list_of_matches, key=len))           
        else:
            if print_output: print(test_string, "\t is VIOLATING:",completed,", failed to match", failed)
            if get_failed:
                return (detect_violation, completed, failed)
            else:
                return detect_violation

    #Static method, can be used outside of the class as well. Maybe rename this to just get_primitives()
    def initialize_primitives(input_string,primitives = None):
        if primitives is None:
            return list(set(input_string))
        else:
            return primitives

    def split_unit_open(unit,primitives):
        # We have two list of strings, the primitives and the perception. 
        # What we want our endresult to be is a list that contains the elements used to build the perception.
        # Any perumtation that can be made from the primitives that is still part of the unit

        #Start by breaking down the percept to its primitives. 
        used_primitives = [primitive for primitive in primitives if primitive in unit]
        final_list = []
        # first traveerse back, and remove used units one by one until it there is nothing left.
        temp_forward = unit
        temp_backwards = unit
        count_forwards = 1
        count_backwards = 1
        while temp_backwards != "" and temp_forward !="":
            #Backwards
            if temp_backwards[-count_backwards:] in used_primitives:
                temp_backwards = temp_backwards[:-count_backwards]
                if temp_backwards:
                    final_list.append(temp_backwards)
            else:
                count_backwards += 1
            #Forwards
            if temp_forward[:count_forwards] in used_primitives:
                temp_forward = temp_forward[count_forwards:]
                if temp_forward:
                    final_list.append(temp_forward)
            else:
                count_forwards += 1
        #final_list.extend(used_primitives)
        return final_list
    #Is not readingFrame ready, or it handles it implicitly based on the primitives. 
    def split_unit(self,unit):
        # We have two list of strings, the primitives and the perception. 
        # What we want our endresult to be is a list that contains the elements used to build the perception.
        # Any perumtation that can be made from the primitives that is still part of the unit

        #Start by breaking down the percept to its primitives. 
        used_primitives = [primitive for primitive in self.primitives if primitive in unit]
        final_list = []
        # first traveerse back, and remove used units one by one until it there is nothing left.
        temp_forward = unit
        temp_backwards = unit
        count_forwards = 1
        count_backwards = 1
        while temp_backwards != "" and temp_forward !="":
            #Backwards
            if temp_backwards[-count_backwards:] in used_primitives:
                temp_backwards = temp_backwards[:-count_backwards]
                if temp_backwards:
                    final_list.append(temp_backwards)
            else:
                count_backwards += 1
            #Forwards
            if temp_forward[:count_forwards] in used_primitives:
                temp_forward = temp_forward[count_forwards:]
                if temp_forward:
                    final_list.append(temp_forward)
            else:
                count_forwards += 1
        #final_list.extend(used_primitives)
        return final_list

    def build_from_substrings(self,possible_matches, input_string):
        if input_string in possible_matches:
            return input_string,"", {input_string:input_string}
        else:
            #We need confirmation that all substrings in the list below are in the vocabulary
            matches = {}
            substrings_to_complete = self.make_list_of_substring(input_string)
            completed = ''
            failed = ''
            for index, substring in enumerate(substrings_to_complete):
                matches[substring] = [percept for percept in possible_matches if substring in percept]
                if matches[substring]:
                    completed += self.find_prim(substring)
                    if index == len(substrings_to_complete)-1:
                        completed += substring[len(self.find_prim(substring)):]
                else:
                    completed += '[]'
                    failed += '['+substring+']'

            return  completed, failed, matches
    
    def make_list_of_substring(self, input_string):
        first_prim = ""
        second_prim = ""
        substring_list = []
        while input_string != "":
            #print(input_string)
            first_prim = self.find_prim(input_string)
            second_prim = self.find_prim(input_string[len(first_prim):])
            substring_list.append(first_prim+second_prim)
            #print("fp: ",first_prim)
            #print("p: ",second_prim)
            #print(input_string[len(first_prim)+len(second_prim):])
            if len(input_string[len(first_prim)+len(second_prim):]) ==0:
                return substring_list
            else:
                input_string = input_string[len(first_prim):]

    def find_prim(self,input_string):
        if len(input_string) == 1:
            return input_string
        for index in range(len(input_string)):
            if input_string[:index] in self.primitives:
                return input_string[:index]
        return input_string

    def get_default_parameters():
        """ Returns the default parameters of the PARSER Model.
            The default parameters as described in the paper PARSER: A Model for Word Segmenetation 
            Returns:
                (Dictionary{String: X})     -- A dictionary containing strings as keys and something else as values. 
            Possible Parameters: 
                shaping_threshold   -- (int/float/) The threshold which a percept has to have to be perceieved from a stream. 
                add_shaped_weight   -- (float) The weight that is added to a percieved unit (if it is not new) and its sub-components
                new_unit_weight     -- (float) The weight that is added to a new perceived unit that does not exist in the percept shaper
                forgetting_weight   -- (float) The weight that is added (should be a negative number) when the percept shaper forgets
                interference_weight -- (float) The weight that is added (should be a negative number) when interference happens in the percept shaper
                min_percept_size    -- (int) The minimum number of percepts that should be perceieved one round (should be at least 1)
                max_percept_size    -- (int) The maximum number of percept that should be perceieved on round. 
                run_type            -- (String) Defines what type of run you want to run
                                        * -- end_of_stream: (Default) Runs until the stream is empty 
                                        * -- single : Runs a single run of the model 
                                        * -- number_of_runs: Runs a X number of runs, requires added parameter number_of_runs. 
                number_of_runs      -- (int) Conditional: Only check if run_type == 'number_of_runs'
                preset              --(bool) Never used at the moment. Maybe implemented at a later stage. 
                random_seed         -- (int) Sets the random seed if one would like reproducability of an experiment.
                logging             -- [bool, int], If on, then the run function loggs every X run.
        """
        return {'shaping_threshold': 1,
                'add_shaped_weight':0.5,
                'new_unit_weight':1,
                'forgetting_weight': -0.05, #In temp its -0.0005
                'interference_weight': -0.005, #in temp its -0.00005,
                'min_percept_size':1,
                'max_percept_size':3,
                'run_type':'end_of_stream'}


    primitives =property(get_primitives,set_primitives)
    random =property(get_random,set_random)
    random_seed =property(get_random_seed,set_random_seed)
    parameters = property(get_parameters, set_parameters)
    percept_shaper = property(get_percept_shaper, set_percept_shaper)                