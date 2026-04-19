import os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + '/..')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

df = pd.read_csv('results/proteins_annotated.csv')
df = df[df['best_score'].notna()]

# Figure 1 — Druggability overview
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('ResistAI — Druggability Analysis of 144 Antibiotic Resistance Proteins', fontsize=14, fontweight='bold')
order = df.groupby('family')['best_score'].mean().sort_values(ascending=False).index
colors = {'TB resistance': '#2ecc71', 'Efflux pump': '#27ae60',
          'Cell wall': '#f39c12', 'Other resistance': '#e67e22',
          'Beta-lactamase': '#e74c3c', 'Other': '#95a5a6',
          'Fluoroquinolone': '#c0392b', 'Aminoglycoside': '#922b21'}
sns.boxplot(data=df, x='family', y='best_score', order=order,
            hue='family', palette=colors, legend=False, ax=axes[0])
axes[0].set_xticks(range(len(order)))
axes[0].set_xticklabels(order, rotation=45, ha='right')
axes[0].set_title('Druggability Score by Resistance Family')
axes[0].set_ylabel('Best Druggability Score')
axes[0].set_xlabel('')
axes[0].axhline(0.7, color='green', linestyle='--', alpha=0.5, label='High threshold')
axes[0].axhline(0.4, color='orange', linestyle='--', alpha=0.5, label='Medium threshold')
axes[0].legend(fontsize=8)
axes[1].hist(df['best_score'], bins=20, color='#3498db', edgecolor='white', alpha=0.8)
axes[1].axvline(0.7, color='green', linestyle='--', label='High (>=0.7)')
axes[1].axvline(0.4, color='orange', linestyle='--', label='Medium (>=0.4)')
axes[1].set_title('Distribution of Druggability Scores')
axes[1].set_xlabel('Best Druggability Score')
axes[1].set_ylabel('Number of Proteins')
axes[1].legend()
high   = len(df[df['best_score'] >= 0.7])
medium = len(df[(df['best_score'] >= 0.4) & (df['best_score'] < 0.7)])
low    = len(df[df['best_score'] < 0.4])
axes[2].pie([high, medium, low],
            labels=[f'High\n(n={high})', f'Medium\n(n={medium})', f'Low\n(n={low})'],
            colors=['#2ecc71', '#f39c12', '#e74c3c'],
            autopct='%1.1f%%', startangle=90)
axes[2].set_title('Druggability Tier Distribution\n(n=144 proteins)')
plt.tight_layout()
plt.savefig('results/figure1_druggability_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print('[OK] Figure 1 saved')

# Figure 2 — Top 20 proteins
top20 = df.nlargest(20, 'best_score').reset_index(drop=True)
fig, ax = plt.subplots(figsize=(14, 10))
colors2 = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' for s in top20['best_score']]
ax.barh(range(len(top20)), top20['best_score'], color=colors2, edgecolor='white')
ax.set_yticks(range(len(top20)))
ax.set_yticklabels([f"{row['gene']} ({row['uniprot_id']})" for _, row in top20.iterrows()], fontsize=11)
ax.set_xlabel('Best Druggability Score', fontsize=12)
ax.set_title('Top 20 Most Druggable Antibiotic Resistance Proteins', fontsize=14, fontweight='bold')
ax.axvline(0.7, color='green', linestyle='--', alpha=0.7, label='High (>=0.7)')
ax.axvline(0.4, color='orange', linestyle='--', alpha=0.7, label='Medium (>=0.4)')
ax.set_xlim(0, 1.15)
ax.legend(fontsize=11)
for i, row in top20.iterrows():
    ax.text(row['best_score'] + 0.01, i, f"{row['best_score']:.3f}", va='center', fontsize=10)
plt.tight_layout()
plt.savefig('results/figure2_top20_proteins.png', dpi=300, bbox_inches='tight')
plt.close()
print('[OK] Figure 2 saved')

# Figure 3 — Heatmap
pivot = df.groupby('family')[['high_druggability','medium_druggability','low_druggability']].sum()
pivot.columns = ['High', 'Medium', 'Low']
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
fig, ax = plt.subplots(figsize=(10, 7))
sns.heatmap(pivot, annot=True, fmt='d', cmap='YlOrRd',
            linewidths=0.5, ax=ax, cbar_kws={'label': 'Number of Pockets'})
ax.set_title('Pocket Druggability Distribution by Resistance Family', fontsize=14, fontweight='bold')
ax.set_xlabel('Druggability Tier', fontsize=12)
ax.set_ylabel('Resistance Family', fontsize=12)
plt.tight_layout()
plt.savefig('results/figure3_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print('[OK] Figure 3 saved')

# Figure 4 — Organism distribution
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
org_counts = df['organism'].value_counts().head(15)
axes[0].barh(range(len(org_counts)), org_counts.values, color='#3498db', edgecolor='white')
axes[0].set_yticks(range(len(org_counts)))
axes[0].set_yticklabels([o[:35] for o in org_counts.index], fontsize=9)
axes[0].set_xlabel('Number of Proteins')
axes[0].set_title('Top 15 Organisms by Protein Count', fontsize=12, fontweight='bold')
org_drug = df.groupby('organism')['best_score'].agg(['mean','count'])
org_drug = org_drug[org_drug['count'] >= 3].sort_values('mean', ascending=False).head(15)
colors3 = ['#2ecc71' if s >= 0.7 else '#f39c12' if s >= 0.4 else '#e74c3c' for s in org_drug['mean']]
axes[1].barh(range(len(org_drug)), org_drug['mean'], color=colors3, edgecolor='white')
axes[1].set_yticks(range(len(org_drug)))
axes[1].set_yticklabels([o[:35] for o in org_drug.index], fontsize=9)
axes[1].set_xlabel('Mean Druggability Score')
axes[1].set_title('Mean Druggability Score by Organism\n(min. 3 proteins)', fontsize=12, fontweight='bold')
axes[1].axvline(0.7, color='green', linestyle='--', alpha=0.5)
axes[1].axvline(0.4, color='orange', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('results/figure4_organisms.png', dpi=300, bbox_inches='tight')
plt.close()
print('[OK] Figure 4 saved')