import json
import re

def clean_output(outputs):
    text_out = []
    for out in outputs:
        if out['output_type'] == 'stream':
            text_out.append(''.join(out.get('text', [])))
        elif out['output_type'] == 'execute_result' or out['output_type'] == 'display_data':
            if 'data' in out and 'text/plain' in out['data']:
                text_out.append(''.join(out['data']['text/plain']))
    return '\n'.join(text_out)

with open('CERT-x466-003_MAIN.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

current_section = "INITIAL"
sections = {
    "EDA": [],
    "ML": [],
    "DL": [],
    "FORECASTING": [],
    "OTHER": []
}

for cell in nb['cells']:
    source = ''.join(cell.get('source', []))
    
    # Check for section headers
    if cell['cell_type'] == 'markdown':
        if re.search(r'#+\s*(?:EXPLORATORY DATA ANALYSIS|EDA)', source, re.IGNORECASE):
            current_section = "EDA"
        elif re.search(r'#+\s*MACHINE LEARNING', source, re.IGNORECASE):
            current_section = "ML"
        elif re.search(r'#+\s*DEEP LEARNING', source, re.IGNORECASE):
            current_section = "DL"
        elif re.search(r'#+\s*FORECASTING', source, re.IGNORECASE):
            current_section = "FORECASTING"
            
    if current_section in sections:
        sections[current_section].append(f"--- {cell['cell_type'].upper()} ---\n{source}")
        if cell['cell_type'] == 'code' and cell.get('outputs'):
            out_text = clean_output(cell['outputs'])
            if out_text.strip():
                # Truncate very long outputs to save context
                if len(out_text) > 1000:
                    out_text = out_text[:1000] + "\n...[TRUNCATED]"
                sections[current_section].append(f"--- OUTPUT ---\n{out_text}")

with open('src/eda_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(sections['EDA']))
    
with open('src/ml_dl_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(sections['ML']))
    f.write('\n\n=== DEEP LEARNING ===\n\n')
    f.write('\n\n'.join(sections['DL']))
    
with open('src/forecasting_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(sections['FORECASTING']))

print("Extraction complete. Summaries saved to src/")
