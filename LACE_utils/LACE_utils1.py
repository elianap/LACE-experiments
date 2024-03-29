#!/usr/bin/env python -W ignore::DeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
import Orange
import os
from copy import deepcopy
import itertools
import matplotlib.pyplot as plt
import numpy as np
from sys import argv
import pickle
import json 
import time
import operator
import subprocess
import operator
import functools
from collections import Counter


def import_dataset_N_evaluations(dataname, n_insts, randomic, datasetExplain=False):
    if datasetExplain:
        return import_datasets(dataname, n_insts, randomic, datasetExplain)
    else:
        return import_dataset(dataname, n_insts, randomic)

def import_dataset(dataname, n_insts, randomic):
    if(dataname[-4:]=="arff"):
        dataset=loadARFF(dataname)
    else:
        dataset=Orange.data.Table(dataname)
    len_dataset=len(dataset)
    list_a=list(range(0,len_dataset))

    if randomic:
        import random
        random.seed(42)
        n_insts=list(random.sample(range(len_dataset), 100))

    n_insts_int=list(map(int, n_insts))
    for i_remove in n_insts_int:
        list_a.remove(i_remove)
    training_dataset=Orange.data.Table.from_table_rows(dataset, list_a)
    len_training_dataset=len(training_dataset)
    explain_dataset=Orange.data.Table.from_table_rows(dataset, n_insts_int)
    return training_dataset, explain_dataset, len_training_dataset, n_insts

def import_datasets(dataname, n_insts, randomic, datasetExplain):

    if(dataname[-4:]=="arff"):
        dataset=loadARFF(dataname)
        dataname_to_explain=dataname[:-5]+"_explain.arff"
        dataset_to_explain=loadARFF(dataname_to_explain)
    else:
        dataset=Orange.data.Table(dataname)
        dataname_to_explain=dataname[:-5]+"_explain"
        dataset_to_explain=Orange.data.Table(dataname_to_explain)
    len_dataset=len(dataset)

    len_dataset_to_explain=len(dataset_to_explain)

    if randomic:
        import random
        random.seed(42)
        n_insts=list(random.sample(range(len_dataset_to_explain), 100))

    n_insts_int=list(map(int, n_insts))

    explain_dataset=Orange.data.Table.from_table_rows(dataset_to_explain, n_insts_int)

    training_dataset=deepcopy(dataset)
    return training_dataset, explain_dataset, len_dataset, n_insts




def toARFF(filename, table, try_numericize=0):
    """Save class:`Orange.data.Table` to file in Weka's ARFF format"""
    t = table
    if filename[-5:] == ".arff":
        filename = filename[:-5]
    #print( filename
    f = open(filename + '.arff', 'w')
    f.write('@relation %s\n' % t.domain.class_var.name)
    # attributes
    ats = [i for i in t.domain.attributes]
    ats.append(t.domain.class_var)
    for i in ats:
        real = 1
        if i.is_discrete == 1:
            if try_numericize:
                # try if all values numeric
                for j in i.values:
                    try:
                        x = float(j)
                    except:
                        real = 0 # failed
                        break
            else:
                real = 0
        iname = str(i.name)
        if iname.find(" ") != -1:
            iname = "'%s'" % iname
        if real == 1:
            f.write('@attribute %s real\n' % iname)
        else:
            f.write('@attribute %s { ' % iname)
            x = []
            for j in i.values:
                s = str(j)
                if s.find(" ") == -1:
                    x.append("%s" % s)
                else:
                    x.append("'%s'" % s)
            for j in x[:-1]:
                f.write('%s,' % j)
            f.write('%s }\n' % x[-1])
    f.write('@data\n')
    for j in t:
        x = []
        for i in range(len(ats)):
            s = str(j[i])
            if s.find(" ") == -1:
                x.append("%s" % s)
            else:
                x.append("'%s'" % s)
        for i in x[:-1]:
            f.write('%s,' % i)
        f.write('%s\n' % x[-1])

def loadARFF_Weka(filename, **kwargs):
    if not os.path.exists(filename) and os.path.exists(filename + ".arff"):
        filename = filename + ".arff"
    f = open(filename, 'r')
    attributes = []
    attributeLoadStatus = []
    name = ''
    state = 0 # header
    data = []
    for l in f.readlines():
        l = l.rstrip("\n\r") # strip trailing whitespace
        l = l.replace('\t', ' ') # get rid of tabs
        x = l.split('%')[0] # strip comments
        if len(x.strip()) == 0:
            continue
        if state == 0 and x[0] != '@':
            print(("ARFF import ignoring:", x))
        if state == 1:
            if x[0] == '{':#sparse data format, begin with '{', ends with '}'
                r = [None] * len(attributes)
                dd = x[1:-1]
                dd = dd.split(',')
                for xs in dd:
                    y = xs.split(" ")
                    if len(y) != 2:
                        raise ValueError("the format of the data is error")
                    r[int(y[0])] = y[1]
                data.append(r)
            else:#normal data format, split by ','
                dd = x.split(',')
                r = []
                for xs in dd:
                    y = xs.strip(" ")
                    if len(y) > 0:
                        if y[0] == "'" or y[0] == '"':
                            r.append(xs.strip("'\""))
                        else:
                            ns = xs.split()
                            for ls in ns:
                                if len(ls) > 0:
                                    r.append(ls)
                    else:
                        r.append('?')
                data.append(r[:len(attributes)])
        else:
            y = []
            for cy in x.split(' '):
                if len(cy) > 0:
                    y.append(cy)
            if str.lower(y[0][1:]) == 'data':
                state = 1
            elif str.lower(y[0][1:]) == 'relation':
                name = str.strip(y[1])                
            elif str.lower(y[0][1:]) == 'attribute':
                if y[1][0] == "'":
                    atn = y[1].strip("' ")
                    idx = 1
                    while y[idx][-1] != "'":
                        idx += 1
                        atn += ' ' + y[idx]
                    atn = atn.strip("' ")
                else:
                    atn = y[1]
                z = x.split('{')
                w = z[-1].split('}')
                if len(z) > 1 and len(w) > 1:
                    # there is a list of values
                    vals = []
                    for y in w[0].split(','):
                        sy = y.strip(" '\"")
                        if len(sy) > 0:
                            vals.append(sy)
                    a= Orange.data.DiscreteVariable.make(atn, vals, True, 0)
                else:
                    # real...
                    a = Orange.data.variable.ContinuousVariable.make(atn, [])
                attributes.append(a)
                #attributeLoadStatus.append(s)
    # generate the domain
    if attributes[-1].name==name:
        d = Orange.data.Domain(attributes[:-1], attributes[-1])
    else:
        new_attr=[]
        for att in attributes:
            if att!=name:
                new_attr.append(att)
            else:
                class_target=att
        d = Orange.data.Domain(new_attr, att)
    lex = []
    for dd in data:
        e = Orange.data.Instance(d, dd)
        lex.append(e)
    t = Orange.data.Table(d, lex)
    t.name = name
    return t

def loadARFF(filename, **kwargs):
    """Return class:`Orange.data.Table` containing data from file in Weka ARFF format
       if there exists no .xml file with the same name. If it does, a multi-label
       dataset is read and returned.
    """
    if filename[-5:] == ".arff":
        filename = filename[:-5]
    if os.path.exists(filename + ".xml") and os.path.exists(filename + ".arff"):
        xml_name = filename + ".xml"
        arff_name = filename + ".arff"
        return Orange.multilabel.mulan.trans_mulan_data(xml_name, arff_name)
    else:
        return loadARFF_Weka(filename)

def printTree(classifier, name):
    features_names=get_features_names(classifier)
    from io import StringIO 
    import pydotplus
    dot_data = StringIO()
    from sklearn import tree
    if features_names!=None:
        tree.export_graphviz(classifier.skl_model, out_file=dot_data, feature_names=features_names, filled=True, rounded=True, special_characters=True)
    else:
        tree.export_graphviz(classifier.skl_model, out_file=dot_data, filled=True, rounded=True, special_characters=True)
    
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf(name+"_tree.pdf")

def get_features_names(classifier):
    features_names=[]
    for i in range(0, len(classifier.domain.attributes)):
        if ">" in classifier.domain.attributes[i].name:
            features_names.append(classifier.domain.attributes[i].name.replace(">", "gr"))

        elif "<" in classifier.domain.attributes[i].name:
            features_names.append(classifier.domain.attributes[i].name.replace("<", "low"))
        else:
            features_names.append(classifier.domain.attributes[i].name)

    return features_names

def getClassifier(training_dataset, args,exit):
        classif=args["classifier"]
        classifier=None
        reason=args
        if classif == "tree":
            if(args["classifierparameter"]==None):
                measure="gini"
            else:
                measure=args["classifierparameter"].split("-")[0]
            if(measure) != "gini" and (measure) != "entropy":
                measure="entropy"
            continuizer = Orange.preprocess.Continuize()
            continuizer.multinomial_treatment = continuizer.Indicators
            learnertree=Orange.classification.SklTreeLearner(preprocessors=continuizer,max_depth = 7, min_samples_split=5,min_samples_leaf=3, random_state=1)
            #learnertree=Orange.classification.SklTreeLearner(preprocessors=continuizer, random_state=1)
          
            classifier=learnertree(training_dataset)
           
            printTree(classifier, training_dataset.name)
            
            

        elif classif == "nb":
            learnernb=Orange.classification.NaiveBayesLearner()
            classifier = learnernb(training_dataset)

        elif classif == "nn":
            continuizer = Orange.preprocess.Continuize()
            continuizer.multinomial_treatment=continuizer.Indicators
            learnernet=Orange.classification.NNClassificationLearner(preprocessors=continuizer, random_state=42)
            
            classifier=learnernet(training_dataset)


        elif classif=="rf":
            import random
            continuizer = Orange.preprocess.Continuize()
            continuizer.multinomial_treatment=continuizer.Indicators
            learnerrf=Orange.classification.RandomForestLearner(preprocessors=continuizer, random_state=42)
            classifier=learnerrf(training_dataset)

        elif classif=="svm":
            import random
            learnerrf=Orange.classification.SVMLearner(preprocessors=continuizer)
            classifier=learnerrf(training_dataset)

        elif classif=="knn":
            if args["classifierparameter"]==None:
                exit=1
                reason="KNN - missing the K parameter"
            elif (len(args["classifierparameter"].split("-"))==1):
                KofKNN=int(args["classifierparameter"].split("-")[0])
                distance=""
            else:
                KofKNN=int(args["classifierparameter"].split("-")[0])
                distance=args["classifierparameter"].split("-")[1] 
            if exit!=1:
                if distance=="eu":
                    metricKNN='euclidean'
                elif distance=="ham":  
                    metricKNN='hamming'      
                elif distance=="man":
                    metricKNN='manhattan'
                elif distance=="max":
                    metricKNN='maximal'
                else:
                    metricKNN='euclidean'
                continuizer = Orange.preprocess.Continuize()
                continuizer.multinomial_treatment=continuizer.Indicators
                knnLearner = Orange.classification.KNNLearner(preprocessors=continuizer, n_neighbors=KofKNN, metric=metricKNN, weights='uniform', algorithm='auto', metric_params=None)
                classifier=knnLearner(training_dataset)
        else:
            reason="Classification model not available"
            exit=1

        return classifier, exit, reason

def useExistingModel(args):
    import os
    if os.path.exists("./models")==False:
        os.makedirs("./models")
    m=""
    if args["classifierparameter"]!=None:
        m="-"+args["classifierparameter"]
    file_path="./models/"+args["dataset"]+"-"+args["classifier"]+m
    if(os.path.exists(file_path)==True):
        with open(file_path, "rb") as f:
            model = pickle.load(f)
        modelname=""
        if args["classifier"] == "tree":
            modelname = "<class 'Orange.classification.tree.SklTreeClassifier'>"
        elif args["classifier"] == "nb":
            modelname = "<class 'Orange.classification.naive_bayes.NaiveBayesModel'>"
        elif args["classifier"] == "nn":
            modelname="<class 'Orange.classification.base_classification.SklModelClassification'>"
        elif args["classifier"]=="knn":
            modelname="<class 'Orange.classification.base_classification.SklModelClassification'>"
        elif args["classifier"]=="rf":
            modelname="<class 'Orange.classification.random_forest.RandomForestClassifier'>"
        else:
            return False
    
        if str(type(model))==modelname:
            return model

    return False

def createDir(outdir):
    try:
        os.makedirs(outdir)
    except:
        pass
