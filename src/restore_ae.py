import json

def update_notebook():
    with open('CERT-x466-003_MAIN.ipynb', 'r') as f:
        nb = json.load(f)
    
    new_code = [
        "ae_input = keras.Input(shape=(n_ae_features,), name='ae_input')\n",
        "\n",
        "# --- Encoder ---\n",
        "x = layers.Dense(128, activation='silu')(ae_input)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.1)(x)\n",
        "\n",
        "x = layers.Dense(64, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "x = layers.Dense(32, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.1)(x)\n",
        "\n",
        "# --- Bottleneck (Linear activation maximizes representation space) ---\n",
        "bottleneck = layers.Dense(8, activation='linear', name='bottleneck')(x)\n",
        "\n",
        "# --- Decoder ---\n",
        "x = layers.Dense(32, activation='silu')(bottleneck)\n",
        "x = layers.BatchNormalization()(x)\n",
        "x = layers.Dropout(0.1)(x)\n",
        "\n",
        "x = layers.Dense(64, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "x = layers.Dense(128, activation='silu')(x)\n",
        "x = layers.BatchNormalization()(x)\n",
        "\n",
        "ae_output = layers.Dense(n_ae_features, activation='linear', name='reconstruction')(x)\n",
        "\n",
        "autoencoder = keras.Model(inputs=ae_input, outputs=ae_output)\n",
        "autoencoder.compile(optimizer=keras.optimizers.AdamW(learning_rate=0.001, weight_decay=1e-4), loss='mse')\n"
    ]

    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and 'ae_input' in ''.join(cell['source']) and 'bottleneck' in ''.join(cell['source']):
            src = cell['source']
            idx1 = next(i for i, line in enumerate(src) if 'ae_input = keras.Input' in line)
            # Find where to stop replacing (usually the encoder definition line)
            idx2 = next(i for i, line in enumerate(src) if "encoder = keras.Model(inputs=ae_input, outputs=autoencoder.get_layer('bottleneck').output" in line)
            
            # Keep before and after
            cell['source'] = src[:idx1] + new_code + src[idx2:]
            break

    with open('CERT-x466-003_MAIN.ipynb', 'w') as f:
        json.dump(nb, f, indent=1)
        f.write('\n')

update_notebook()
