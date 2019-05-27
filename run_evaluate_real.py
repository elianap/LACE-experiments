import subprocess
datasets = ['compas-scores-two-years_d.arff', 'adult_d.arff']
models = ['nn', 'nb', 'rf']
dataset_targetClass={"compas-scores-two-years_d.arff":"High", 'adult_d.arff':"<=50K"}
dataset_instance={"compas-scores-two-years_d.arff":"1443", 'adult_d.arff':"0"}
for dataset in datasets:
    for model in models:
        outfile = '%s-%s.log' % (dataset, model)
        cmd = 'python -W ignore LACE_method.py -d %s -c %s -i %s -cl %s -eType -dE'% ("datasets/"+dataset, model,dataset_instance[dataset],dataset_targetClass[dataset])
        with open(outfile,"wb") as out:
        	subprocess.Popen(cmd.split(),stdout=out).wait()