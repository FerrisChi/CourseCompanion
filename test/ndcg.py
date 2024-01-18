import numpy as np

def calculate_ndcg(relevance_scores):
    # Calculate DCG
    DCG = np.sum([rel / np.log2(idx + 2) for idx, rel in enumerate(relevance_scores)])
    
    # Calculate IDCG
    sorted_scores = sorted(relevance_scores, reverse=True)
    IDCG = np.sum([rel / np.log2(idx + 2) for idx, rel in enumerate(sorted_scores)])
    
    # Avoid division by zero in case of IDCG being zero
    if IDCG == 0:
        return 0
    
    # Calculate NDCG
    NDCG = DCG / IDCG
    return NDCG

ss4 = [
    [3, 3, 2, 1, 2],
    [3, 1, 3, 3, 2],
    [3, 2, 2, 1, 1],
    [2, 3, 3, 2, 1],
    [1, 2, 2, 2, 2],
    [2, 3, 2, 2, 1],
    [3, 2, 2, 1, 0],
    [3, 2, 2, 3, 2]
]

ss35 = [
    [3, 2, 1, 2, 3],
    [2, 2, 3, 2, 1],
    [2, 2, 0, 1, 0],
    [3, 2, 2, 1, 2],
    [2, 1, 1, 2, 1],
    [3, 2, 0, 2, 2],
    [1, 1, 2, 3, 3],
]

ndcg4 = [calculate_ndcg(ss) for ss in ss4]
ndcg35 = [calculate_ndcg(ss) for ss in ss35]
print("NDCG for gpt4:", sum(ndcg4)/len(ndcg4))
print("NDCG for gpt35:", sum(ndcg35)/len(ndcg35))