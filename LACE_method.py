#!/usr/bin/env python -W ignore::DeprecationWarning
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from LACE_utils.LACE_utils1 import *
from LACE_utils.LACE_utils2 import *
from LACE_utils.LACE_utils3 import *
from LACE_utils.LACE_utils4 import *
from LACE_utils.LACE_utils5 import *


def parserArg():
    import argparse
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-d','--dataset', help='Input dataset', required=True)
    parser.add_argument('-c','--classifier', help='Classifier', required=True)
    parser.add_argument('-cp','--classifierparameter', help='Classifier')
    parser.add_argument('-k','--Kneighbors', help='Number of neighbors', required=False)
    parser.add_argument('-cl','--classname', help='Name of the target class', required=True)
    parser.add_argument('-s','--save', help='Save the model', action='store_true')
    parser.add_argument('-u','--use', help='Use, possibly, a already existing model', action='store_true')
    parser.add_argument("-i", "--instancesId", help="Ids of the instances to be explained, comma separated")
    parser.add_argument('-eType','--experimentType', help='Evaluate', required=False, action='store_true')
    parser.add_argument('-dE','--explainDataset', help='Explanation dataset', required=False, action='store_true')
    parser.add_argument('-th','--threshold', help='Threshold for approximate error', required=False)
    parser.add_argument('-maxKNN','--maxKNN', help='Max value of K for KNN', required=False)

    return parser


if(len(argv)<4):
    print( "- d dataset, - c classifier, -cl classname, -i instanceIdToBeExplained, [-cp measure], [-k K for local model] ")
else:    
    parser=parserArg() 
    args = vars(parser.parse_args())
    dataname=args["dataset"]   
    n_insts=args["instancesId"].split(",")
    classname=args["classname"]
    classif=args["classifier"]
    evaluateExpl = args["experimentType"]
    present=False  
    


    #Temporary folder 
    import uuid
    unique_filename = str(uuid.uuid4())
    exit=0

    if evaluateExpl:
    	training_dataset, explain_dataset, len_dataset, n_insts=import_dataset_N_evaluations(dataname, n_insts, evaluateExpl, args["explainDataset"])
    else:
    	training_dataset, explain_dataset, len_dataset, n_insts=import_dataset(dataname, n_insts, evaluateExpl)

    K_NN, threshold, maxN=getUserDefined(args, len_dataset)

    #If the user specifies to use an existing model, the model is used (if available). Otherwise it is trained.
    if args["use"]==True:
        #"Check if the model exist...
        classifier=useExistingModel(args)
        if classifier!=False:
            present=True
            #The model exists, we'll use it
        #The model does not exist, we'll train it")
    if args["use"]==False or present==False:
        classifier, exit, reason=getClassifier(training_dataset, args,exit)
   
    if exit!=1:
        #Save the model only if required and it is not already saved.
        if args["save"]==True and present==False:
            #"Saving the model..." 
            m=""
            if args["classifierparameter"]!=None:
                m="-"+args["classifierparameter"]
            createDir("./models")    
            with open("./models/"+dataname+"-"+classif+m, "wb") as f:
                pickle.dump(classifier, f)

        map_names_class={}
        num_i=0
        for i in training_dataset.domain.class_var.values[:]:
            map_names_class[num_i]=i
            num_i=num_i+1


        #Correspondence classname-pos_number
        indexI=-1
        for i in training_dataset.domain.class_var.values[:]:
            indexI=indexI+1
            if i==classname:
                break

        NofClass=len(training_dataset.domain.class_var.values[:])

        #Compute the neighbors of the instanceId
        from sklearn.neighbors import NearestNeighbors
        metricKNNA='euclidean'
        NearestNeighborsAll = NearestNeighbors(n_neighbors=len(training_dataset), metric=metricKNNA, algorithm='auto', metric_params=None).fit(training_dataset.X)

        oldinputAr=[]
        oldMappa={}
        mappa_single={}

        firstInstance=1


        startingK=K_NN
        
        mappa_class=computeMappaClass_b(training_dataset)
        count_inst=-1
        map_instance_apprE={}
        map_instance_NofKNN={}
        map_instance_1_apprE={}
        map_instance_diff_approxFirst={}



        for Sn_inst in n_insts:
            count_inst=count_inst+1
            old_impo_rules=[]
            firstKNN=True
            oldError=10.0
            n_inst2=int(Sn_inst)
            instTmp2 = Orange.data.Instance(explain_dataset.domain, explain_dataset[count_inst])
            c=classifier(instTmp2, False)

            startingK=K_NN
            #Problem with very small training dataset. The starting KNN is low, very few examples: difficult to capture the locality.
            #Risks: examples too similar, only 1 class. Starting K: proportional to the class frequence
            small_dataset_len=150
            if len_dataset<small_dataset_len:
                startingK=max(int(mappa_class[map_names_class[c[0]]]*len_dataset), startingK)

            plot=False
            for NofKNN in range (startingK, maxN, K_NN):
                #DO TO MULTIPLE
                n_inst=int(Sn_inst) 
                instTmp = Orange.data.Instance(explain_dataset.domain, explain_dataset[count_inst])
                instT=deepcopy(instTmp)

                genNeighborsInfo(training_dataset, NearestNeighborsAll, explain_dataset.X[count_inst], n_inst, NofKNN, unique_filename, classifier)

                #Call L3
                subprocess.call(['java', '-jar', 'AL3.jar', '-no-cv', '-t','./'+unique_filename+'/Knnres.arff', '-T', './'+unique_filename+'/Filetest.arff', '-S', '1.0', '-C', '50.0', '-PN', "./"+unique_filename, '-SP', '10', '-NRUL', '1'] )


                datanamepred="./"+unique_filename+"/gen-k0.arff"
                with open ("./"+unique_filename+"/impo_rules.txt", "r") as myfile:
                    impo_rules=myfile.read().splitlines()

                #The local model is not changed
                if set(impo_rules)==set(old_impo_rules) and firstKNN==False:
                    continue



                old_impo_rules=impo_rules[:]

                impo_rules_N=[]

                reduceOverfitting=False
                for impo_r in impo_rules:
                    #Not interested in a rule composed of all the attributes values. By definition, its relevance is prob(y=c)-prob(c)
                    if len(impo_r.split(","))!=len(instTmp.domain.attributes):
                            impo_rules_N.append(impo_r)

                impo_rules=impo_rules_N[:]

                
                inputAr, nInputAr, newInputAr, oldAr_set=getRelevantSubsetFromLocalRules(impo_rules, oldinputAr)

                impo_rules_complete=deepcopy(inputAr)


                #Compute probability of Single attribute or Set of Attributes
                firstInstance=0
                mappaNew={}
                mappa=oldMappa.copy()
                mappa.update(mappaNew)

                

                if firstKNN:
                    c1=classifier(instT, True)[0]
                    pred=c1[indexI]
                    pred_str=str(round(c1[indexI], 2))
                    out_data= computePredictionDifferenceSinglever2(instT, classifier, indexI, training_dataset)


                map_difference={}
                map_difference=computePredictionDifferenceSubsetRandomOnlyExisting(training_dataset, instT, inputAr, classname, classifier, indexI, map_difference)

                #Definition of approximation error. How we approximate the "true explanation"?
                error_single, error, PI_rel2=computeApproxError(mappa_class,pred,out_data, impo_rules_complete, classname, map_difference)


                minlen, minlenname, minvalue= getMinRelevantSet(instT, impo_rules_complete, map_difference)


                oldinputAr=inputAr+oldinputAr
                oldinputAr_set = set(map(tuple,oldinputAr)) 
                oldMappa.update(mappa)
                if firstKNN:
                    map_instance_1_apprE[n_inst]=PI_rel2
                    map_instance_diff_approxFirst[n_inst]=error
                    map_instance_apprE[n_inst]=PI_rel2
                    map_instance_NofKNN[n_inst]=NofKNN

                #if (error)*100<threshold:
                threshold=0.02
                if (error)<threshold:
                    #final
                    if not(evaluateExpl):
                        plotTheInfo(instT, out_data, impo_rules, n_inst, dataname, NofKNN, "f", minlenname, minvalue, classname, error, error_single, classif, map_difference, impo_rules_complete, pred_str)
                    map_instance_apprE[n_inst]=PI_rel2
                    map_instance_NofKNN[n_inst]=NofKNN
                    printImpoRuleInfo(n_inst, NofKNN, out_data,map_difference,impo_rules_complete, impo_rules)
                    plot=True
                    break
                #local minimum 
                elif (abs(error)-abs(oldError))>0.01 and firstKNN==False:
                    #PLOT OLD ERROR AS BETTER
                    if not(evaluateExpl):
                        plotTheInfo(instT, old_out_data, old_impo_rulesPlot, n_inst, dataname, oldNofKNN, "f", minlenname, minvalue, classname, oldError, error_single, classif, old_map_difference, old_impo_rules_complete, pred_str)
                    plot=True
                    map_instance_apprE[n_inst]=PI_rel2_old
                    map_instance_NofKNN[n_inst]=oldNofKNN
                    printImpoRuleInfo(n_inst, oldNofKNN, old_out_data,old_map_difference,old_impo_rules_complete, old_impo_rulesPlot)
                    break
                else:
                    firstKNN=False
                    oldError=error
                    oldNofKNN=NofKNN
                    old_out_data=deepcopy(out_data)
                    old_impo_rulesPlot=deepcopy(impo_rules)
                    old_map_difference=deepcopy(map_difference)
                    old_impo_rules_complete=deepcopy(impo_rules_complete)
                    PI_rel2_old=PI_rel2

            
            #if NofKNN>=(maxN-startingK):   
            if NofKNN>=(maxN) or plot==False:
                if (error)==(oldError):
                    if not(evaluateExpl):
                        plotTheInfo(instT, old_out_data, old_impo_rulesPlot, n_inst, dataname, oldNofKNN, "f", minlenname, minvalue, classname, oldError, error_single, classif, old_map_difference, old_impo_rules_complete, pred_str)
                    map_instance_apprE[n_inst]=PI_rel2_old
                    map_instance_NofKNN[n_inst]=oldNofKNN
                    printImpoRuleInfo(n_inst, oldNofKNN, old_out_data,old_map_difference,old_impo_rules_complete,old_impo_rulesPlot)

                else:
                    if not(evaluateExpl):
                        plotTheInfo(instT, out_data, impo_rules, n_inst, dataname, NofKNN, "f", minlenname, minvalue, classname, error, error_single, classif, map_difference, impo_rules_complete, pred_str)
                    map_instance_apprE[n_inst]=PI_rel2
                    map_instance_NofKNN[n_inst]=NofKNN
                    printImpoRuleInfo(n_inst, out_data,map_difference,impo_rules_complete,impo_rules)


        #Remove the temporary folder and dir
        import shutil
        if os.path.exists("./"+unique_filename):
            shutil.rmtree("./"+unique_filename)

        for k in map_instance_NofKNN.keys():
            map_instance_NofKNN[k]=map_instance_NofKNN[k]/startingK

        avg, minv, maxv=getmap_instance_NofKNNIterationInfo(map_instance_NofKNN)
        print("KNN-Info, avg, min, max", avg, minv, maxv)
        
    

        getInfoError(map_instance_apprE, map_instance_1_apprE, dataname, classif)






    else: 
        print( "Exit -", reason)