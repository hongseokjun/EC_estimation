import os
import numpy as np
import scipy.stats as stt
import matplotlib.pyplot as pp

os.system('clear')

graph_format = 'png'

obj_dir = './'
res_dir = 'res_movie/'

# network parameters
n_sub = 22 # number of subjects
n_cond = 2 # rest and movie conditions
N = 66 # size of network

i_tau = 1 # tau used in optimization (to adjust according to optimization_movie.py)


# load empirical FC and ROI labels
FC_emp = np.load(res_dir+'FC_emp.npy')
ROI_labels = np.load(obj_dir+'ROI_labels.npy')

# masks
mask_EC = np.load(res_dir+'mask_EC.npy')
mask_Sigma = np.load(res_dir+'mask_Sigma.npy')


# load results
EC_mod = np.load(res_dir+'EC_mod.npy')
Sigma_mod = np.load(res_dir+'Sigma_mod.npy')
FC0_mod = np.load(res_dir+'FC0_mod.npy')
FCtau_mod = np.load(res_dir+'FCtau_mod.npy')


# fit and consistency
dist_FC_fit = np.zeros([n_sub,n_cond])
Pearson_FC_fit = np.zeros([n_sub,n_cond])

Pearson_FC0_emp = np.zeros([n_sub*(n_sub-1)/2,n_cond])
Pearson_EC = np.zeros([n_sub*(n_sub-1)/2,n_cond])

for i_cond in range(n_cond):
	cnt_tmp = 0
	for i_sub1 in range(n_sub):
		dist_FC_fit[i_sub1,i_cond] = 0.5*(np.sqrt(np.sum((FC0_mod[i_sub1,i_cond,:,:]-FC_emp[i_sub1,i_cond,0,:,:])**2)/np.sum((FC_emp[i_sub1,i_cond,0,:,:])**2))+np.sqrt(np.sum((FCtau_mod[i_sub1,i_cond,:,:]-FC_emp[i_sub1,i_cond,i_tau,:,:])**2)/np.sum((FC_emp[i_sub1,i_cond,i_tau,:,:])**2)))
		Pearson_FC_fit[i_sub1,i_cond] = 0.5*(stt.pearsonr(FC_emp[i_sub1,i_cond,0,:,:].reshape(-1),FC0_mod[i_sub1,i_cond,:,:].reshape(-1))[0]+stt.pearsonr(FC_emp[i_sub1,i_cond,1,:,:].reshape(-1),FCtau_mod[i_sub1,i_cond,:,:].reshape(-1))[0])
		for i_sub2 in range(i_sub1):
			Pearson_FC0_emp[cnt_tmp,i_cond] = stt.pearsonr(FC_emp[i_sub1,i_cond,0,:,:].reshape(-1),FC_emp[i_sub2,i_cond,0,:,:].reshape(-1))[0]
			Pearson_EC[cnt_tmp,i_cond] = stt.pearsonr(EC_mod[i_sub1,i_cond,mask_EC],EC_mod[i_sub2,i_cond,mask_EC])[0]
			cnt_tmp += 1


print
print 'consistency'
print 'Pearson FC0 emp (rest, movie):', Pearson_FC0_emp.mean(0), '; std:', Pearson_FC0_emp.std(0)
print 'Pearson EC (rest, movie):', Pearson_EC.mean(0), '; std', Pearson_EC.std(0)



pp.figure()
pp.boxplot(dist_FC_fit,positions=[0,1])
pp.xticks([0,1],['black','movie'],fontsize=9)
pp.ylabel('dist FC fit')
pp.savefig(res_dir+'dist_FC_fit.'+graph_format,format=graph_format)
pp.close()

pp.figure()
pp.boxplot(Pearson_FC_fit,positions=[0,1])
pp.xticks([0,1],['black','movie'],fontsize=9)
pp.ylabel('Pearson FC fit')
pp.savefig(res_dir+'Pearson_FC_fit.'+graph_format,format=graph_format)
pp.close()

pp.figure()
pp.plot(Pearson_EC[:,0],Pearson_FC0_emp[:,0],'xb')
pp.plot(Pearson_EC[:,1],Pearson_FC0_emp[:,1],'xr')
pp.xlabel('Pearson EC')
pp.ylabel('Pearson FC0 emp')
pp.savefig(res_dir+'Pearson_FC_vs_Pearson_EC.'+graph_format,format=graph_format)
pp.close()



print
print 'significance test for changes in input variances on diagonal of Sigma across conditions (pval<0.01 uncorrected):'
for i in range(N):
	if stt.ttest_ind(Sigma_mod[:,0,i,i],Sigma_mod[:,1,i,i],equal_var=False)[1]<0.01:
		print ROI_labels[i], ' with mean change', np.mean(Sigma_mod[:,1,i,i]-Sigma_mod[:,0,i,i])


print
print 'significance test of changes in EC across conditions (pval<0.01 uncorrected):'
for i in range(N):
	for j in range(N):
		if mask_EC[i,j] and stt.ttest_ind(EC_mod[:,0,i,j],EC_mod[:,1,i,j],equal_var=False)[1]<0.01:
			print ROI_labels[j], '->', ROI_labels[i], ' with mean change', np.mean(EC_mod[:,1,i,j]-EC_mod[:,0,i,j])
