# fragments
import pandas as pd
import numpy as np

def cartesian_product(*arrays):
    grid = np.array(np.meshgrid(*arrays, indexing='ij'))
    cartesian_prod = np.stack(grid, axis=-1).reshape(-1, len(arrays))
    return cartesian_prod

# PMF
ta_p=[0.11, 0.89]
tb_p=[0.11, 0.89]
skills_cartesian = cartesian_product(ta_p, tb_p)
values = np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    (skills_cartesian[:, 0] * skills_cartesian[:, 1]).reshape(-1, 1)))
                             
pmf = pd.DataFrame(data=values, columns=['ta', 'tb', 'p'])
pmf['p'] = pmf['p'].astype('float64')

# fragment 1
# P(X1|ta,tb)
tasks_p_1 = pd.DataFrame(data=np.hstack((
    cartesian_product([1, 0], ['h', 'l'], ['h', 'l']),
    np.hstack((
        [0.99, 0.90, 0.90, 0.01], #x1 = 1
        [0.01, 0.10, 0.10, 0.99], #x1 = 0
    )).reshape(-1, 1)
)),
                       columns=['outcome', 'ta', 'tb', 'p'])
tasks_p_1['p'] = tasks_p_1['p'].astype('float64')


p_theta_1 = pd.DataFrame(data=np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    np.ones((4, 1)))),
                         columns=['ta', 'tb', 'p'])
p_theta_1['p'] = p_theta_1['p'].astype('float64')
emf_1 = np.hstack((p_theta_1['p'], p_theta_1['p'])) * tasks_p_1['p']

# evidence arrives X1=1
# step 1
p_theta_1_old = pmf['p']

# step 2, set x1=0 to 0
tasks_p_1.loc[tasks_p_1['outcome'] == '0', 'p'] = 0

# step 3
p_theta_1_new = tasks_p_1[tasks_p_1['outcome'] == '1']['p']

# step 4
proportion = p_theta_1_new / p_theta_1_old
pmf['p'] = pmf['p'] * proportion
pmf['p'] = pmf['p'] / pmf['p'].sum()

# fragment 1 can be discarded as no longer useful

# fragment 2
skills_combinations = cartesian_product([1, 0], ['h', 'l'], ['h', 'l'])
tasks_p_2 = pd.DataFrame(data=np.hstack((
    skills_combinations,
    np.hstack((
        [0.99, 0.05, 0.90, 0.01], #x2 = 1
        [0.01, 0.95, 0.10, 0.99], #x2 = 0
    )).reshape(-1, 1)
)),
                       columns=['outcome', 'ta', 'tb', 'p'])
tasks_p_2['p'] = tasks_p_2['p'].astype('float64')

p_theta_2 = pd.DataFrame(data=np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    np.ones((4, 1)))),
                         columns=['ta', 'tb', 'p'])
p_theta_2['p'] = p_theta_2['p'].astype('float64')


emf_2 = pd.DataFrame(data=np.hstack((
    skills_combinations,
    (np.hstack((p_theta_2['p'], p_theta_2['p'])) * tasks_p_2['p']).values.reshape(-1, 1)
)),
                    columns=['outcome', 'ta', 'tb', 'p'])

emf_2['p'] = emf_2['p'].astype('float64')

print(emf_2)
# predict step 1
# footprints of both tasks are equal, nothing needs to be done
p_theta_2_new = pmf['p']

# predict step 2
p_theta_2_old = p_theta_2['p']
proportion = (p_theta_2_new / p_theta_2_old).astype('float64')


# predict step 3
emf_2['p'] = (np.hstack((proportion, proportion)) * emf_2['p']).values.reshape(-1, 1)

# normalize
p_sum = emf_2['p'].sum()
emf_2['p']= emf_2['p'] / p_sum
print(f"emf_2 updated \n{emf_2}")
print(f"pmf updated: \n{pmf}")
# fragments
import pandas as pd
import numpy as np

def cartesian_product(*arrays):
    grid = np.array(np.meshgrid(*arrays, indexing='ij'))
    cartesian_prod = np.stack(grid, axis=-1).reshape(-1, len(arrays))
    return cartesian_prod

# PMF
ta_p=[0.11, 0.89]
tb_p=[0.11, 0.89]
skills_cartesian = cartesian_product(ta_p, tb_p)
pmf = pd.DataFrame(data=np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    (skills_cartesian[:, 0] * skills_cartesian[:, 1]).reshape(-1, 1))),
                             columns=['ta', 'tb', 'p'])
pmf['p'] = pmf['p'].astype('float64')

# fragment 1
# P(X1|ta,tb)
tasks_p_1 = pd.DataFrame(data=np.hstack((
    cartesian_product([1, 0], ['h', 'l'], ['h', 'l']),
    np.hstack((
        [0.99, 0.90, 0.90, 0.01], #x1 = 1
        [0.01, 0.10, 0.10, 0.99], #x1 = 0
    )).reshape(-1, 1)
)),
                       columns=['outcome', 'ta', 'tb', 'p'])
tasks_p_1['p'] = tasks_p_1['p'].astype('float64')


p_theta_1 = pd.DataFrame(data=np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    np.ones((4, 1)))),
                         columns=['ta', 'tb', 'p'])
p_theta_1['p'] = p_theta_1['p'].astype('float64')
emf_1 = np.hstack((p_theta_1['p'], p_theta_1['p'])) * tasks_p_1['p']

# evidence arrives X1=1
# step 1
p_theta_1_old = pmf['p']

# step 2, set x1=0 to 0
tasks_p_1.loc[tasks_p_1['outcome'] == '0', 'p'] = 0

# step 3
p_theta_1_new = tasks_p_1[tasks_p_1['outcome'] == '1']['p']

# step 4
proportion = p_theta_1_new / p_theta_1_old
pmf['p'] = pmf['p'] * proportion
pmf['p'] = pmf['p'] / pmf['p'].sum()

# fragment 1 can be discarded as no longer useful

# fragment 2
skills_combinations = cartesian_product([1, 0], ['h', 'l'], ['h', 'l'])
tasks_p_2 = pd.DataFrame(data=np.hstack((
    skills_combinations,
    np.hstack((
        [0.99, 0.05, 0.90, 0.01], #x2 = 1
        [0.01, 0.95, 0.10, 0.99], #x2 = 0
    )).reshape(-1, 1)
)),
                       columns=['outcome', 'ta', 'tb', 'p'])
tasks_p_2['p'] = tasks_p_2['p'].astype('float64')

p_theta_2 = pd.DataFrame(data=np.hstack((
    cartesian_product(['h', 'l'], ['h', 'l']),
    np.ones((4, 1)))),
                         columns=['ta', 'tb', 'p'])
p_theta_2['p'] = p_theta_2['p'].astype('float64')


emf_2 = pd.DataFrame(data=np.hstack((
    skills_combinations,
    (np.hstack((p_theta_2['p'], p_theta_2['p'])) * tasks_p_2['p']).values.reshape(-1, 1)
)),
                    columns=['outcome', 'ta', 'tb', 'p'])

emf_2['p'] = emf_2['p'].astype('float64')

print(emf_2)
# predict step 1
# footprints of both tasks are equal, nothing needs to be done
p_theta_2_new = pmf['p']

# predict step 2
p_theta_2_old = p_theta_2['p']
proportion = (p_theta_2_new / p_theta_2_old).astype('float64')


# predict step 3
emf_2['p'] = (np.hstack((proportion, proportion)) * emf_2['p']).values.reshape(-1, 1)

# normalize
p_sum = emf_2['p'].sum()
emf_2['p']= emf_2['p'] / p_sum
print(f"emf_2 updated \n{emf_2}")
print(f"pmf updated: \n{pmf}")
