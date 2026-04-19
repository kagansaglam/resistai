import pandas as pd
import numpy as np
from scipy import stats
import json
import os

# Load summary report
df = pd.read_csv('results/summary_report.csv')

# Load gene info from pathogens.csv
meta = pd.read_csv('data/pathogens.csv')
df = df.merge(meta, on='uniprot_id', how='left')

# Categorise by resistance family
def categorise(gene):
    if not isinstance(gene, str):
        return 'Other'
    g = gene.lower()
    if any(x in g for x in ['kpc','ndm','oxa','vim','imp','bla','ctx','shv','tem','ampc','cpha','ccra']):
        return 'Beta-lactamase'
    if any(x in g for x in ['van','meca','pbp']):
        return 'Cell wall'
    if any(x in g for x in ['aac','aph','ant','eis','aac']):
        return 'Aminoglycoside'
    if any(x in g for x in ['mex','ade','acr','opr','mdt']):
        return 'Efflux pump'
    if any(x in g for x in ['katg','inha','rpob']):
        return 'TB resistance'
    if any(x in g for x in ['gyra','parc','gyra']):
        return 'Fluoroquinolone'
    if any(x in g for x in ['tet','cat','sul','dhps']):
        return 'Other resistance'
    return 'Other'

df['family'] = df['gene'].apply(categorise)

print('=== Family Distribution ===')
print(df['family'].value_counts())
print()

print('=== Druggability by Family (mean ± std) ===')
stats_df = df.groupby('family')['best_score'].agg(['mean','std','count'])
stats_df = stats_df.sort_values('mean', ascending=False)
print(stats_df.round(3))
print()

# ANOVA — is there significant difference between families?
groups = [g['best_score'].values for _, g in df.groupby('family') if len(g) >= 3]
f_stat, p_value = stats.f_oneway(*groups)
print(f'=== One-way ANOVA ===')
print(f'F-statistic : {f_stat:.3f}')
print(f'p-value     : {p_value:.4f}')
if p_value < 0.05:
    print('Result      : Significant difference between families (p < 0.05)')
else:
    print('Result      : No significant difference (p >= 0.05)')
print()

# Pairwise t-tests between top families
print('=== Pairwise t-tests (top families) ===')
families = stats_df[stats_df['count'] >= 5].index.tolist()
for i in range(len(families)):
    for j in range(i+1, len(families)):
        a = df[df['family']==families[i]]['best_score']
        b = df[df['family']==families[j]]['best_score']
        t, p = stats.ttest_ind(a, b)
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        print(f'{families[i]:<20} vs {families[j]:<20} p={p:.4f} {sig}')

# Save results
df.to_csv('results/proteins_annotated.csv', index=False)
print()
print('[OK] Annotated dataset saved to results/proteins_annotated.csv')