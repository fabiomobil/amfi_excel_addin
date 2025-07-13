#!/usr/bin/env python3
"""
Script para corrigir imports em todos os arquivos do monitor/utils
para serem compatíveis com Spyder
"""

import os
import re

def fix_relative_imports(file_path):
    """
    Corrige imports relativos em um arquivo Python para serem compatíveis com Spyder
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Padrão para encontrar imports relativos
    import_pattern = r'^from \.([\w_]+) import (.+)$'
    
    # Lista de todos os imports relativos encontrados
    relative_imports = re.findall(import_pattern, content, re.MULTILINE)
    
    if not relative_imports:
        print(f"✓ {os.path.basename(file_path)}: Nenhum import relativo encontrado")
        return False
    
    print(f"🔧 {os.path.basename(file_path)}: Encontrados {len(relative_imports)} imports relativos")
    
    # Substituir imports relativos por um sistema mais robusto
    new_imports = []
    modules_imported = {}
    
    for module, items in relative_imports:
        if module not in modules_imported:
            modules_imported[module] = []
        modules_imported[module].extend([item.strip() for item in items.split(',')])
    
    # Gerar novo bloco de imports
    import_block = "# Sistema de imports compatível com Spyder e outros ambientes\n"
    import_block += "import sys\n"
    import_block += "import os\n\n"
    
    # Adicionar tentativa de imports
    import_block += "# Tentar imports relativos primeiro\n"
    import_block += "try:\n"
    for module, items in modules_imported.items():
        items_str = ', '.join(items)
        import_block += f"    from .{module} import {items_str}\n"
    import_block += "except (ImportError, ValueError):\n"
    import_block += "    # Fallback para imports diretos (Spyder)\n"
    import_block += "    if os.path.dirname(__file__) not in sys.path:\n"
    import_block += "        sys.path.insert(0, os.path.dirname(__file__))\n"
    for module, items in modules_imported.items():
        items_str = ', '.join(items)
        import_block += f"    from {module} import {items_str}\n"
    
    # Remover imports relativos antigos e adicionar novos
    lines = content.split('\n')
    new_lines = []
    skip_next = False
    imports_added = False
    
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        if re.match(import_pattern, line):
            if not imports_added:
                # Adicionar novo bloco de imports na primeira ocorrência
                new_lines.append(import_block.rstrip())
                imports_added = True
            # Pular linha do import relativo antigo
            continue
        elif line.strip().startswith('# Imports locais') or line.strip().startswith('# Imports dos novos'):
            # Pular comentários de imports
            continue
        else:
            new_lines.append(line)
    
    new_content = '\n'.join(new_lines)
    
    # Salvar arquivo corrigido
    backup_path = file_path + '.bak'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ {os.path.basename(file_path)}: Imports corrigidos, backup salvo como .bak")
    return True


# Arquivos para corrigir
utils_dir = "monitor/utils"
files_to_fix = [
    "file_loaders.py",
    "data_handler.py", 
    "alerts.py",
    "file_discovery.py",
    "data_converters.py"
]

print("🔍 Corrigindo imports nos arquivos do monitor/utils...\n")

for file_name in files_to_fix:
    file_path = os.path.join(utils_dir, file_name)
    if os.path.exists(file_path):
        fix_relative_imports(file_path)
    else:
        print(f"❌ {file_name}: Arquivo não encontrado")

print("\n✨ Correção de imports concluída!")