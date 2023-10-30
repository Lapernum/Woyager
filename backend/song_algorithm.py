import numpy as np

def tag_sim_score(tag_dict1=None, tag_dict2=None):
    '''
    This function calculates the similarity score between two dictionary of tags.
    
    Input:
    tag_dict1: a (tag, count) pair dictionary
    tag_dict2: a (tag, count) pair dictionary

    Output:
    score: a float number representing similarity
    '''
    all_keys = set(tag_dict1.keys()) | set(tag_dict2.keys())
    # print(all_keys)
    t1 = np.zeros(len(all_keys))
    t2 = np.zeros(len(all_keys))
    for i, key in enumerate(all_keys):
        if key in tag_dict1:
            t1[i] = tag_dict1[key]
        if key in tag_dict2:
            t2[i] = tag_dict2[key]
    
    prod = np.dot(t1, t2)
    norm1 = np.linalg.norm(t1)
    norm2 = np.linalg.norm(t2)
    return prod / (norm1 * norm2)


def main():
    tag1 = {1: 100, 3: 96, 5: 77, 14: 40}
    tag2 = {1: 100, 2: 80, 3: 60, 4: 30}
    score = tag_sim_score(tag1, tag2)
    print(score)
    tag3 = {1: 100, 2: 70, 3: 50}
    tag4 = {1: 100, 2: 70, 3: 50}
    tag5 = {1: 100, 3: 95, 2: 67}
    score2 = tag_sim_score(tag3, tag4)
    score3 = tag_sim_score(tag4, tag5)
    print(score2)
    print(score3)

if __name__ == "__main__":
    main()