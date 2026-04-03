import json
import os
import glob


PATH_JSON_GT = "./dataset_en/json" 
PATH_SQL_GT = "./dataset_en/sql_ground_truth"

if not os.path.exists(PATH_SQL_GT):
    os.makedirs(PATH_SQL_GT)


def clean_name(name):
    return name.replace(" ", "_").upper()


def translate_to_sql_robust(json_data):
    ddl_statements = []
    newline_indent = ",\n  "
    
    # Tabelle per entità
    for entity in json_data.get('entities', []):
        table_name = clean_name(entity['name'])
        cols = []
        pks = []
        
        for attr in entity.get('attributes', []):
            col_name = clean_name(attr['name'])
            cols.append(f"{col_name} VARCHAR(255)")
            if attr.get('is_pk'):
                pks.append(col_name)
        
        cols_str = newline_indent.join(cols)
        sql = f"CREATE TABLE {table_name} (\n  {cols_str}"
        
        if pks: 
            pk_str = ", ".join(pks)
            sql += f",\n  PRIMARY KEY ({pk_str})"
        sql += "\n);"
        ddl_statements.append(sql)

    # Gestione relazioni
    for rel in json_data.get('relationships', []):
        entities_involved = []
        for i in range(1, 4):
            key = f'entity{i}'
            if key in rel and rel[key]:
                entities_involved.append(clean_name(rel[key]))
        
        cardinality = rel.get('cardinality', '1:N')
        rel_attributes = rel.get('attributes', [])

        if len(entities_involved) > 2 or cardinality == "N:M":
            rel_name = clean_name(rel.get('name', f"REL_{'_'.join(entities_involved)}"))
            cols = []
            fks = []
            for ent in entities_involved:
                col_name = f"FK_{ent}"
                cols.append(f"{col_name} VARCHAR(255)")
                fks.append(f"FOREIGN KEY ({col_name}) REFERENCES {ent}")
            
            for ra in rel_attributes:
                cols.append(f"{clean_name(ra['name'])} VARCHAR(255)")

            cols_str = newline_indent.join(cols)
            pks_bridge = ", ".join([c.split()[0] for c in cols if 'FK_' in c])
            fks_str = newline_indent.join(fks)
            
            sql = f"CREATE TABLE {rel_name} (\n  {cols_str},\n  PRIMARY KEY ({pks_bridge}),\n  {fks_str}\n);"
            ddl_statements.append(sql)
            
        elif cardinality == "1:N" and len(entities_involved) >= 2:
            e1 = entities_involved[0] 
            e2 = entities_involved[1] 
            
            alter_queries = []
            alter_queries.append(f"ALTER TABLE {e2} ADD COLUMN FK_{e1} VARCHAR(255)")
            alter_queries.append(f"ALTER TABLE {e2} ADD CONSTRAINT FK_{e2}_{e1} FOREIGN KEY (FK_{e1}) REFERENCES {e1}")
            
            for ra in rel_attributes:
                alter_queries.append(f"ALTER TABLE {e2} ADD COLUMN {clean_name(ra['name'])} VARCHAR(255)")
            
            ddl_statements.append(";\n".join(alter_queries) + ";")

    return "\n\n".join(ddl_statements)


# Loop di esecuzione con FILTRO
files = glob.glob(os.path.join(PATH_JSON_GT, "*.json"))

# FILTRO: escludiamo i file che finiscono con _M.json o _MT.json
files_da_processare = [f for f in files if not f.endswith("_M.json") and not f.endswith("_MT.json")]
print(f"Trovati {len(files)} file totali. Processerò solo {len(files_da_processare)} file originali.")

for path_file in files_da_processare:
    try:
        with open(path_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sql_script = translate_to_sql_robust(data)
        nome_output = os.path.basename(path_file).replace('.json', '.sql')
        with open(os.path.join(PATH_SQL_GT, nome_output), 'w', encoding='utf-8') as out_f:
            out_f.write(sql_script)
    except Exception as e:
        print(f"Errore nel file {path_file}: {e}")

print("Ground Truth SQL generato con successo!")
