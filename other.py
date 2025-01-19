
# %%
import seaborn as sns

# Apply the default theme
sns.set_theme()

# Load an example dataset
tips = sns.load_dataset("tips")
sns.relplot(data=tips, kind="line", x="total_bill", y='tip')
# %%
