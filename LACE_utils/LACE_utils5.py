#!/usr/bin/env python -W ignore::DeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from LACE_utils.LACE_utils1 import *

def computePredictionDifferenceSubsetRandomOnlyExisting(dataset, instT, inputA, classname, classifier, indexI, mappa_sum_v2):

    inst=deepcopy(instT)
    mappa_attr_index={}

    listaval_v2=[]
    for v1 in inputA[:]:
        listaval1=[]
        for v2 in v1[:]:
            n=0 
            for k in dataset.domain.attributes[:]:
                n=n+1
                if n==v2:                    
                    listaval1.append(k)
        if (len(listaval1))>1:
            listaval_v2.append(listaval1)
            mappa_attr_index[','.join(map(str, listaval1))]=','.join(map(str, v1))


    for g_v2 in listaval_v2[:]:
        d=Orange.data.Table()
        g_v2_a_i=Orange.data.Domain(g_v2)
        filtered_i=d.from_table(g_v2_a_i, dataset)
        c = Counter(map(tuple, filtered_i.X))
        freq=dict(c.items())

        for k_ex in freq:
            inst1=deepcopy(instT)
            for v in range(0, len(g_v2)):
                inst1[g_v2_a_i[v]]=k_ex[v]
            
            name=[j.name for j in g_v2]
            combinations=functools.reduce(operator.mul, [len(i.values) for i in g_v2])

            setIndex= mappa_attr_index[','.join(map(str, name))]
            if setIndex not in mappa_sum_v2:
                mappa_sum_v2[setIndex]=0.0
            c0=classifier(inst1, False)[0]
            c1=classifier(inst1, True)[0]


            prob=0.000000
            prob=c1[indexI]
            newvalue=prob*freq[k_ex]/len(dataset)
            mappa_sum_v2[setIndex]=mappa_sum_v2[setIndex]+newvalue


    
    c0=classifier(inst, False)[0]
    c1=classifier(inst, True)[0]

    prob=c1[indexI]

    for key, value in mappa_sum_v2.items():
        mappa_sum_v2[key]=prob-mappa_sum_v2[key]

    return  mappa_sum_v2



#Single explanation. Change 1 value at the time e compute the difference
def computePredictionDifferenceSinglever2(instT, classifier, indexI, dataset):
    from copy import deepcopy
    i=deepcopy(instT)
    listaoutput=[]

    c0=classifier(i, False)[0]
    c1=classifier(i, True)[0]
    prob=c1[indexI]

    for u in i.domain.attributes[:]:
        listaoutput.append(0.0)

    t=-1
    for k in dataset.domain.attributes[:]:
        d=Orange.data.Table()
        t=t+1
        k_a_i=Orange.data.Domain([k])
        filtered_i=d.from_table(k_a_i, dataset)
        c = Counter(map(tuple, filtered_i.X))
        freq=dict(c.items())

        for k_ex in freq:
            inst1=deepcopy(instT)
            inst1[k]=k_ex[0]            
            c1=classifier(inst1, True)[0]

            prob=0.000000
            prob=c1[indexI]
            test=freq[k_ex]/len(dataset)
            #newvalue=prob*freq[k_ex]/len(dataset)
            newvalue=prob*test
            listaoutput[t]=listaoutput[t]+newvalue


    l=len(listaoutput)

    for i in range(0,l):
        listaoutput[i]=prob- listaoutput[i]
    return  listaoutput



def getPerc(input_per):
    result_mean_instance={}
    for k in input_per.keys():
        if list(input_per[k].keys())[0]!="":
            result_mean_instance[k]=sum([input_per[k][k2] for k2 in input_per[k]])/len(([input_per[k][k2] for k2 in input_per[k]]))
    mean_per=sum(result_mean_instance[k] for k in result_mean_instance)/len(result_mean_instance)
    result_mean_instanceA={}
    for k in input_per.keys():
        result_mean_instanceA[k]=sum([input_per[k][k2] for k2 in input_per[k]])/len(([input_per[k][k2] for k2 in input_per[k]]))
    mean_per_A=sum(result_mean_instanceA[k] for k in result_mean_instanceA)/len(result_mean_instanceA)
    return mean_per, mean_per_A


def getmap_instance_NofKNNIterationInfo(map_instance_NofKNN):
    sum=0
    for k in map_instance_NofKNN.keys():
        sum=sum+map_instance_NofKNN[k]

    avg=float(sum)/float(len(map_instance_NofKNN))
    minv=min([map_instance_NofKNN[k] for k in map_instance_NofKNN])
    maxv=max([map_instance_NofKNN[k] for k in map_instance_NofKNN])
    return avg, minv, maxv 



def getInfoError(rel, rel1, d, t):
    avg,minv,maxv=getmap_instance_NofKNNIterationInfo(rel)
    avg1,minv1,maxv1=getmap_instance_NofKNNIterationInfo(rel1)
    diff=avg1-avg
    print("Approximation Gain:", diff)


def printImpoRuleInfo(instT, NofKNN, out_data,map_difference,impo_rules_complete, impo_rules):
	print(instT,":  K=", NofKNN, "Rules", impo_rules)
	print("PredDifference", map_difference, out_data, "\n")

