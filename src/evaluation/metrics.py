def accuracy(y_true,y_pred): return sum(a==b for a,b in zip(y_true,y_pred))/len(y_true) if y_true else 0.0

def macro_f1(y_true,y_pred):
    labels=sorted(set(y_true)|set(y_pred)); scores=[]
    for label in labels:
        tp=sum(a==label and b==label for a,b in zip(y_true,y_pred)); fp=sum(a!=label and b==label for a,b in zip(y_true,y_pred)); fn=sum(a==label and b!=label for a,b in zip(y_true,y_pred))
        p=tp/(tp+fp) if tp+fp else 0; r=tp/(tp+fn) if tp+fn else 0; scores.append(2*p*r/(p+r) if p+r else 0)
    return sum(scores)/len(scores) if scores else 0.0

def recall_at_k(relevant,retrieved,k):
    relevant=set(relevant)
    return len(relevant & set(retrieved[:k]))/len(relevant) if relevant else 0.0

def precision_at_k(relevant,retrieved,k):
    if k<=0: return 0.0
    return len(set(relevant)&set(retrieved[:k]))/min(k,len(retrieved)) if retrieved else 0.0

def reciprocal_rank(relevant,retrieved):
    relevant=set(relevant)
    for i,x in enumerate(retrieved,1):
        if x in relevant: return 1/i
    return 0.0

def mean(values): return sum(values)/len(values) if values else 0.0
