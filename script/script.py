import os
import sys
os.chdir("../lib")


def exec(mypar,log):
	cmd = "python3 App.py "
	pars = ""
	for k in mypar: 
		pars+= " -"+str(k)+" "+str(mypar[k])
	cmd = cmd + pars + ' -l ' + str(log)
	lgn = os.system(cmd)
	print(lgn)
	return lgn
	

params = {
        "np": [50,100,200],
        "m" : [0.1,0.3,0.4,0.6,0.8],
        "t" : [3,5,7,10],
        "c" : [1,2,3,4],
        "me" : ["swap","opt"]
        }

params_np_t  =[
        {"np": 50, "t" : 3},
        {"np": 100, "t" : 3},
        {"np" : 150, "t" : 3},
        {"np" : 200, "t" : 3},
        {"np" : 250, "t" : 3},
        {"np" : 300, "t" : 3},
        {"np": 50, "t" : 5},
        {"np": 100, "t" : 5},
        {"np" : 150, "t" : 5},
        {"np" : 200, "t" : 5},
        {"np" : 250, "t" : 5},
        {"np" : 300, "t" : 5},
        {"np": 50, "t" : 7},
        {"np": 100, "t" : 7},
        {"np" : 150, "t" : 7},
        {"np" : 200, "t" : 7},
        {"np" : 250, "t" : 7},
        {"np" : 300, "t" : 7},
        {"np": 50, "t" : 10},
        {"np": 100, "t" : 10},
        {"np" : 150, "t" : 10},
        {"np" : 200, "t" : 10},
        {"np" : 250, "t" : 10},
        {"np" : 300, "t" : 10},
        ]

params_m = []

for j in params["m"]:
	params_m.append({"np": 200, "t" : 8 , "m" : j})

params_c = []

for j in params["c"]:
	params_c.append({"np": 200, "t" : 8 , "c" : j})

for kk in range(len(params_np_t)):
	lg = "tournAndpop_" + str(kk)
	exec(params_np_t[kk], lg)
	
for jj in range(len(params_m)):
	for l in range(4):
		lg = "mutation_"+str(jj)+"-"+str(l)
		exec(params_m[jj], lg)
		

for jj in range(len(params_c)):
	for l in range(4):
		lg = "cross_"+str(jj)+"-"+str(l)
		lgn = exec(params_c[jj], lg)










