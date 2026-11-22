import numpy as np, scipy.sparse as sp, json, sys
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
y_tr=np.load("results/logits/labels.npz")["y_train"].astype(int) if "y_train" in np.load("results/logits/labels.npz").files else None
lab=np.load("/tmp/fix_tok/out/labels.npz"); y_tr=lab["y_train"].astype(int); y_te=lab["y_test"].astype(int)
def bow(x,V=50002):
    n=x.shape[0]; rows=np.repeat(np.arange(n),x.shape[1]); m=x.ravel()!=0
    M=sp.csr_matrix((np.ones(m.sum(),dtype=np.float32),(rows[m],x.ravel()[m])),shape=(n,V)); M.data=np.log1p(M.data); return M
def run(tag,d,drop=None):
    xtr=np.load(d+"/x_train.npy"); xte=np.load(d+"/x_test.npy")
    A,B=bow(xtr),bow(xte)
    if drop is not None:
        keep=np.ones(A.shape[1],bool); keep[drop]=False; A=A[:,keep]; B=B[:,keep]
    clf=LogisticRegression(C=0.5,max_iter=300,solver="liblinear").fit(A,y_tr)
    print(tag,"Jan in-sample AUC %.4f"%roc_auc_score(y_tr,clf.decision_function(A)),"April AUC %.4f"%roc_auc_score(y_te,clf.decision_function(B)),flush=True)
role="/tmp/p3_role/out/role/variants/bpe50k_role"; fix="/tmp/fix_tok/out/variants/bpe50k_fix"


v=json.load(open(role+"/vocab.json")); import re
ids=[i for k,i in v.items() if re.fullmatch(r"▁?addr\d+x[0-9a-f]",k)]
print("role-token ids:",len(ids))

run("addr control",  "/tmp/p3_addr/out/addr/variants/bpe50k_addr")
import glob
for g in glob.glob("/tmp/claude-0/*/*/scratchpad/tune_inputs/variants/bpe50k"): run("old tokenizer",g)
