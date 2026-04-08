import json

def update_notebook():
    with open('CERT-x466-003_MAIN.ipynb', 'r') as f:
        nb = json.load(f)
    
    new_code = [
        "x = layers.Concatenate()(cat_embeddings + [num_input])\n",
        "\n",
        "# --- Deep Tabular MLP with Residual Connections ---\n",
        "# Initial projection to desired width\n",
        "x = layers.Dense(256, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "# Residual Block 1\n",
        "res = x\n",
        "x = layers.Dense(256, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.2)(x)\n",
        "x = layers.Dense(256)(x)\n",
        "x = layers.Add()([res, x])\n",
        "x = layers.Activation('silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "# Residual Block 2 (with dimension reduction)\n",
        "res = layers.Dense(128)(x) # Match dimensions\n",
        "x = layers.Dense(128, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.2)(x)\n",
        "x = layers.Dense(128)(x)\n",
        "x = layers.Add()([res, x])\n",
        "x = layers.Activation('silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "# Residual Block 3 (with dimension reduction)\n",
        "res = layers.Dense(64)(x) # Match dimensions\n",
        "x = layers.Dense(64, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.1)(x)\n",
        "x = layers.Dense(64)(x)\n",
        "x = layers.Add()([res, x])\n",
        "x = layers.Activation('silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "# Final funnel to output\n",
        "x = layers.Dense(32, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.1)(x)\n",
        "x = layers.Dense(16, activation='silu')(x)\n",
        "output = layers.Dense(1, name='salary_output')(x)\n",
        "\n",
        "emb_model = keras.Model(inputs=cat_inputs + [num_input], outputs=output)\n",
        "emb_model.compile(optimizer=keras.optimizers.AdamW(learning_rate=0.001, weight_decay=1e-4), loss='mse', metrics=['mae'])\n"
    ]

    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and 'emb_model = keras.Model' in ''.join(cell['source']):
            src = cell['source']
            idx1 = next(i for i, line in enumerate(src) if 'layers.Concatenate()' in line)
            idx2 = next((i for i, line in enumerate(src) if 'def make_input_dict' in line), len(src))
            
            # Keep before and after
            cell['source'] = src[:idx1] + new_code + src[idx2:]
            break

    with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
        json.dump(nb, f, indent=1)
        f.write('\n')

update_notebook()
