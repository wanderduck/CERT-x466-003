import json

def update_notebook():
    with open('/home/wanderduck/000_Duckspace/WanderduckDevelopment/Ducks/UMN/CERT-x466-003/CERT-x466-003_MAIN.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    new_code = [
        "        self.net = nn.Sequential(\n",
        "            nn.Linear(n_features, 1024),\n",
        "            nn.SiLU(),\n",
        "            nn.BatchNorm1d(1024),\n",
        "            nn.Dropout(0.2),\n",
        "            nn.Linear(1024, 512),\n",
        "            nn.SiLU(),\n",
        "            nn.BatchNorm1d(512),\n",
        "            nn.Dropout(0.2),\n",
        "            nn.Linear(512, 128),\n",
        "            nn.SiLU(),\n",
        "            nn.BatchNorm1d(128),\n",
        "            nn.Dropout(0.1),\n",
        "            nn.Linear(128, 1),\n",
        "        )\n"
    ]

    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            src = cell.get('source', [])
            if any('class SalaryMLP(nn.Module):' in line for line in src):
                idx1 = next(i for i, line in enumerate(src) if 'self.net = nn.Sequential(' in line)
                idx2 = next(i for i, line in enumerate(src) if 'def forward(self, x):' in line)
                
                # We need to keep any blank lines before `def forward`
                end_idx = idx2
                for i in range(idx2 - 1, idx1, -1):
                    if ')' in src[i] and '        )' in src[i]:
                        end_idx = i + 1
                        break
                        
                cell['source'] = src[:idx1] + new_code + src[end_idx:]
                break

    with open('/home/wanderduck/000_Duckspace/WanderduckDevelopment/Ducks/UMN/CERT-x466-003/CERT-x466-003_MAIN.ipynb', 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
        f.write('\n')

update_notebook()
