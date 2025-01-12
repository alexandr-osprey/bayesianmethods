from pgmpy.factors.discrete import TabularCPD, DiscreteFactor
import numpy as np

cpd = TabularCPD('item7', variable_card=2, values=[
            [0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85, 0.85,  0.85, 0.85, 0.080],
            [0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15,  0.15, 0.15, 0.920]
        ], evidence=['s1', 's3', 's4', 's5'], evidence_card=[2,2, 2, 2])


def get_factor( emf: DiscreteFactor, evidence: tuple) -> DiscreteFactor:
        sorted_variables = emf.variables.copy()
        sorted_variables.sort()
        variables_being_sorted = emf.variables.copy()
        values = emf.values.reshape(emf.cardinality)
        for desired_i in range(len(sorted_variables)):
            v = sorted_variables[desired_i]
            i = variables_being_sorted.index(v)
            s = variables_being_sorted[desired_i]
            variables_being_sorted[desired_i] = v
            variables_being_sorted[i] = s
            values = np.moveaxis(values, i, desired_i)

        evidence_var_index = sorted_variables.index(evidence[0])
        sorted_variables.pop(evidence_var_index)
        cardinality = np.delete(emf.cardinality, evidence_var_index)
        values = np.take(values, evidence[1], axis=evidence_var_index)
        factor = DiscreteFactor(sorted_variables, cardinality=cardinality, values=values)
        normalized = factor.normalize(inplace=False)

        return normalized

emf = cpd.to_factor()

factor = get_factor(emf, ('item7', 0))
print(factor.values)