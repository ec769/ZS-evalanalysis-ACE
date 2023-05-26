import json
import argparse

#given an argument, return the list of references to the argument within the same sentence, without duplicates
def coref_inst_in_event(arg,start_index,end_index,entity_clusters):
    coref = []
    for cluster in entity_clusters:
        for tup1 in cluster:
            #check to see if the spans are equal or contain each other
            if ((tup1[0] == arg[0] and tup1[1] == arg[1])  or (tup1[0] <= arg[0] and tup1[1] >= arg[1]) or (tup1[0] >= arg[0] and tup1[1] <= arg[1])):
                #check all of the spans in the cluster
                for tup2 in cluster:
                    if end_index is None:
                        if tup2[0] >= start_index:
                            coref.append(tup2)
                            continue
                    #check to see if the span is within the sentence boundary
                    if tup2[0] >= start_index and tup2[1] <= end_index:
                        coref.append(tup2)
    #remove duplicates: some words may exist multiple times in the same sentence, but we don't want to count these again
    seen = []
    final_coref = []
    for c in coref:
        if c[3].lower() not in seen:
            seen.append(c[3].lower()) 
            final_coref.append(c)
    return final_coref

#Output: count_ner_ref: for how many tuples is a reference a named entity, count_ner_arg: for how many tuples is the argument a named entity
def ner_stats(coref, arg):
    if coref == []:
        check_list = [arg]
    else:
        check_list = coref
    count_ner_ref = 0
    count_ner_arg = 0
    for tup in check_list:
        if ((tup[3][0].isupper()) or (" " in tup[3][0])):
            count_ner_ref = count_ner_ref + 1
            if ((tup[0] == arg[0] and tup[1] == arg[1])  or (tup[0] <= arg[0] and tup[1] >= arg[1]) or (tup[0] >= arg[0] and tup[1] <= arg[1])):
                count_ner_arg = count_ner_arg + 1
    return count_ner_ref, count_ner_arg

#given an argument and list of references in the sentence, check if the argument is the first of the references in the sentence
def first(coref, arg):
    if coref == []:
        return "na"
    for tup in coref:
        if tup[0] < arg[0]:
            return "not first"
    return "first"

#Output: count_pro_ref: for how many tuples is a reference a named entity, count_pro_arg: for how many tuples is the argument a named entity
def pro_stats(coref, arg, option):
    if option == "relative":
        arr = ["whom","who","which","that"]
    else:
        arr = ["he","she","it","him","her","they","them","us","we"]
    if coref == []:
        check_list = [arg]
    else:
        check_list = coref
    count_pro_ref = 0
    count_pro_arg = 0
    for tup in check_list:
        if tup[3].lower() in arr:
            count_pro_ref = count_pro_ref + 1
            if tup[1] == arg[1] and tup[0] == arg[0]:
                count_pro_arg = count_pro_arg + 1
    return count_pro_ref, count_pro_arg
    
def parse(filename):
    arr = []
    with open(filename, "r") as f2r:
        for each_line in f2r:
            dat = json.loads(each_line)
            arr.append(dat)

    sent_event_metadata = []
    args_events_metadata = []
    agg_array = []
    doc_ref = []
    only_event_ref = []
    gather_ne = []
    gather_first = []
    gather_relpro = []
    gather_otherpro = []
    for doc in arr:
        events = doc["events"]
        sentence_starts = doc["_sentence_start"]
        sentence_ref = []
        for i in range(0,len(events)):
            event_ref = []
            if events[i] == []:
                sent_event_metadata.append(0)
            else:
                sent_event_metadata.append(len(events[i]))
                for e in events[i]:
                    args_events_metadata.append(len(e)-1)
                    if len(e) == 1:
                        event_ref.append(0)
                        continue
                    arg_ref = []
                    for arg in e[1:]:
                        start_index = sentence_starts[i]
                        end_index = None
                        if i < len(events)-1:
                            end_index = sentence_starts[i+1]
                        coref = coref_inst_in_event(arg,start_index,end_index,doc["clusters"])
                        if len(coref) > 1:
                            a = ner_stats(coref, arg)
                            b = first(coref,arg)
                            c = pro_stats(coref, arg, "relative")
                            d = pro_stats(coref, arg, "other")
                            gather_ne.append(a)
                            gather_first.append(b)
                            gather_relpro.append(c)
                            gather_otherpro.append(d)
                        only_event_ref.append(len(coref))
                        if len(coref) > 1:
                            arg_ref.append(len(coref))
                    event_ref.append(arg_ref)

    
    print("Number of sentences:",len(sent_event_metadata))
    print("Number of event mentions:",sum(sent_event_metadata))
    print("Number of sentences that contain event mentions:",len(sent_event_metadata)-sent_event_metadata.count(0))
    for i in range(0,10):
        print("Number of event mentions with",i,"arguments:",args_events_metadata.count(i))
    print("Number of arguments over all event mentions:",sum(args_events_metadata))
    print("Number of arguments with 1 reference in the same sentence:",only_event_ref.count(0)+only_event_ref.count(1))
    for i in range(2,7):
        print("Number of arguments with",i,"references in the same sentence:",only_event_ref.count(i))
    arg_not_otherpro = 0
    arg_otherpro = 0
    no_otherpro = 0
    for tup in gather_otherpro:
        if tup[1] == 0 and tup[0] > 0:
            arg_not_otherpro = arg_not_otherpro + 1
        elif tup[1] == 1 and tup[0] > 0:
            arg_otherpro = arg_otherpro + 1
        elif tup[0] == 0 and tup[1] == 0:
            no_otherpro = no_otherpro + 1
        else:
            print(tup)
    print("We call a pronoun in [\"he\",\"she\",\"it\",\"him\",\"her\",\"they\",\"them\",\"us\",\"we\"] as \"other\"")
    print("Of arguments with >1 reference in the same sentence where one of those references is an \"other\" pronoun, the number where the argument is the \"other\" pronoun:",arg_otherpro)
    print("Of arguments with >1 reference in the same sentence where one of those references is an \"other\" pronoun, the number where the argument is NOT the \"other\" pronoun:",arg_not_otherpro)
    print("Of arguments with >1 reference in the same sentence, the number where none of those references is an \"other\" pronoun: ", no_otherpro)
    arg_not_rel = 0
    arg_rel = 0
    no_rel = 0
    for tup in gather_relpro:
        if tup[1] == 0 and tup[0] > 0:
            arg_not_rel = arg_not_rel + 1
        elif tup[1] == 1 and tup[0] > 0:
            arg_rel = arg_rel + 1
        elif tup[0] == 0 and tup[1] == 0:
            no_rel = no_rel + 1
        else:
            print(tup)
    print("We call a pronoun in [\"whom\",\"who\",\"which\",\"that\"] as \"relative\"")
    print("Of arguments with >1 reference in the same sentence where one of those references is a relative pronoun, the number where the argument is the relative pronoun:",arg_rel)
    print("Of arguments with >1 reference in the same sentence where one of those references is an relative  pronoun, the number where the argument is NOT the relative pronoun:",arg_not_rel)
    print("Of arguments with >1 reference in the same sentence, the number where none of those references is an relative  pronoun: ", no_rel)
    arg_first = 0
    arg_not_first = 0
    arg_other = 0
    for val in gather_first:
        if val == "first":
            arg_first = arg_first + 1
        elif val == "not first":
            arg_not_first = arg_not_first + 1
        else:
            arg_other = arg_other + 1 
    print("Of arguments with >1 reference in the same sentence, the number where the argument is first of those references to appear:",arg_first)
    print("Of arguments with >1 reference in the same sentence, the number where the argument is NOT the first of those references to appear:",arg_not_first)
    arg_not_ne = 0
    arg_ne = 0
    no_ne = 0
    for tup in gather_ne:
        if tup[1] == 0 and tup[0] > 0:
            arg_not_ne = arg_not_ne + 1
        elif tup[1] == 1 and tup[0] > 0:
            arg_ne = arg_ne + 1
        elif tup[0] == 0 and tup[1] == 0:
            no_ne = no_ne + 1
    print("Of arguments with >1 reference in the same sentence where one of those references is a named entity, the number where the argument is the named entity:",arg_ne)
    print("Of arguments with >1 reference in the same sentence where one of those references is a named entity, the number where the argument is NOT the named entity:",arg_not_ne)
    print("Of arguments with >1 reference in the same sentence, the number where none of those references is a named entity: ", no_ne)



parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("output_name", help="Name for output directory.")
args = parser.parse_args()
fname = f"./construct-preprocess-data/data/ace-event/processed-data/{args.output_name}/json/data.json"
parse(fname)