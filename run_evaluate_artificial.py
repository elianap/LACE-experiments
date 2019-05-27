import subprocess
datasets = ['monks-1', 'chess.arff', 'group.arff']
models = ['nn', 'nb', 'rf']
dataset_targetClass={"monks-1":"1", 'chess.arff':'Blue', 'group.arff':'Group1', 'monks_extended.arff':0}
dataset_instance={"monks-1":"8", 'chess.arff':0, 'group.arff':0, 'monks_extended.arff':1}
for dataset in datasets:
    for model in models:
        outfile = '%s-%s.log' % (dataset, model)
        if dataset=="monks-1":
        	cmd = 'python -W ignore LACE_method.py -d %s -c %s -i %s -cl %s -eType'% (dataset, model,dataset_instance[dataset],dataset_targetClass[dataset])
        else:
        	cmd = 'python -W ignore LACE_method.py -d %s -c %s -i %s -cl %s -eType'% ("datasets/"+dataset, model,dataset_instance[dataset],dataset_targetClass[dataset])
        with open(outfile,"wb") as out:
        	subprocess.Popen(cmd.split(),stdout=out).wait()