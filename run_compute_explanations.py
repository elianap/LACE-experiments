import subprocess
datasets = ['compas-scores-two-years_d.arff','monks-1','monks_extended.arff']
models = ['nn', 'nb']
dataset_targetClass={"monks-1":"1", "compas-scores-two-years_d.arff":"High", 'monks_extended.arff':0}
dataset_instance={"monks-1":"8", "compas-scores-two-years_d.arff":"1443", 'monks_extended.arff':0}
for dataset in datasets:
    for model in models:
        outfile = '%s-%s.log' % (dataset, model)
        if dataset=="monks-1":
        	cmd = 'python -W ignore LACE_method.py -d %s -c %s -i %s -cl %s'% (dataset, model,dataset_instance[dataset],dataset_targetClass[dataset])
        else:
        	cmd = 'python -W ignore LACE_method.py -d %s -c %s -i %s -cl %s'% ("datasets/"+dataset, model,dataset_instance[dataset],dataset_targetClass[dataset])
        with open(outfile,"wb") as out:
        	subprocess.Popen(cmd.split(),stdout=out).wait()