#!/usr/bin/env python -W ignore::DeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from LACE_utils.LACE_utils1 import *



def getMinRelevantSet(instT, impo_rules_complete, map_difference):        
    minlen=len(instT.domain.attributes)
    minlenname=""
    minvalue=0.0

    impo_rules_completeC = ''.join(str(e)+", " for e in list(impo_rules_complete[0]))
    impo_rules_completeC=impo_rules_completeC[:-2]
    
    if impo_rules_completeC!="":
        if len(impo_rules_completeC.replace(" ", "").split(","))>1:
            for k in map_difference:
                if map_difference[k]== map_difference[impo_rules_completeC.replace(" ", "")]:
                        a=k.split(",")
                        if len(a)<minlen:
                            minlen=len(a)
                            minlenname=k
                            minvalue=map_difference[minlenname]
    return minlen, minlenname, minvalue



#Plot the info
def plotbarh(x, y, title, label, namefig, colour, min_m, max_m):
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    y_pos = np.arange(len(x))

    ax.barh(y_pos, y, align='center',color=colour)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(x)
    if min_m!="f" and max_m!="f":
        ax.set_xlim(min_m*1.2, max_m*1.1)
    ax.invert_yaxis()
    ax.set_title(title)
    ax.set_xlabel(label)
    fig.savefig(namefig, bbox_inches="tight") 
    plt.close()



def getAttrProbSingle(instT, out_data):
    attributes_list=[]
    for i in instT.domain.attributes:
        attributes_list.append(str(i.name+"="+str(instT[i])))

    probSingleNoInt=[]
    probSingleNoInt=deepcopy(out_data)
    return attributes_list, probSingleNoInt


def plotTheInfo(instT, out_data, impo_rules, n_inst, dataname, K, errorFlag, minlenname, minvalue, classname, error, error_single, classif, map_difference, impo_rules_complete, pred_str):
    classname_f=classname

    if ">" in classname:
        classname_f=classname.replace(">", "gr")
    if "<" in classname:
        classname_f=classname.replace("<", "low")

    import os
    cwd = os.getcwd()
    d_folder=os.path.basename(dataname)
    dataname
    print(cwd)
    print(d_folder)

    path=cwd+"/"+d_folder+"_"+classif+"_class_"+classname


    createDir(path)

    attributes_list, probSingleNoInt=getAttrProbSingle(instT, out_data)
    attributes_list_a=deepcopy(attributes_list)
    predDiff=deepcopy(probSingleNoInt)

    #getSingles_Rules():
    a_l_single=[]
    a_l_single=deepcopy(attributes_list)
    list_single_compare=[]
    list_single_compare=deepcopy(probSingleNoInt)
    for k in range(0, len(impo_rules)):
        if len(impo_rules[k].split(","))!=1:
            a_l_single.append(str(impo_rules[k].replace(" ", "")))
            list_single_compare.append(map_difference[impo_rules[k].replace(" ", "")])
            if minlenname!="" and map_difference[impo_rules[k].replace(" ", "")]!=minvalue:
                attributes_list_a.append(str(impo_rules[k].replace(" ", "")))
                predDiff.append(map_difference[impo_rules[k].replace(" ", "")])




    impo_rules_completeC = ''.join(str(e)+"," for e in list(max(impo_rules_complete, key=len)))[:-1]
    list_single_compare_2=[]
    list_single_compare_2=deepcopy(list_single_compare)      
    a_l_single_2=[]
    a_l_single_2=deepcopy(a_l_single)                       
    

    if impo_rules_completeC not in a_l_single_2:
        if len(impo_rules_completeC.split(","))!=1:
            list_single_compare_2.append(map_difference[impo_rules_completeC.replace(" ", "")])
            a_l_single_2.append(str(impo_rules_completeC.replace(" ", "")))
            if map_difference[impo_rules_completeC.replace(" ", "")]!=minvalue:
                predDiff.append(map_difference[impo_rules_completeC.replace(" ", "")])
                attributes_list_a.append(str(impo_rules_completeC.replace(" ", "")))
    


    #Unique min-max, in order to have a common scale.
    min_m=min(list_single_compare_2)
    max_m=max(list_single_compare_2)

    plt.style.use('seaborn-talk')
    title="d="+dataname+" model="+classif+"\n"+"p(class="+classname+"|x)="+pred_str+"   true class= "+str(instT.get_class())
    namefig=classif+"_"+str(n_inst)+"_"+classname+'_K'+str(int(K))
    colour='lightblue'

    label2="Pred. difference single + Pred. difference Rules + Complete- target class="+ classname

    plotbarh(a_l_single_2, list_single_compare_2, title, label2, path+'/SRC_'+namefig+'_singles_rules_complete.png', colour, min_m, max_m)
