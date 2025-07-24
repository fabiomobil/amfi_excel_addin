import ast
import os
import re
from collections import defaultdict

defined_functions = {}
called_functions = defaultdict(int)  # Count occurrences

def extract_functions_from_file(file_path):
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Count lines in function
        lines = content.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('__') and node.name.endswith('__') and node.name != '__init__':
                    continue
                
                # Estimate function size
                end_line = node.lineno
                for child in ast.walk(node):
                    if hasattr(child, 'lineno') and child.lineno > end_line:
                        end_line = child.lineno
                
                function_lines = end_line - node.lineno + 1
                    
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'type': 'function',
                    'class': None,
                    'size': function_lines
                })
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith('__') and item.name.endswith('__') and item.name != '__init__':
                            continue
                        
                        # Estimate method size
                        end_line = item.lineno
                        for child in ast.walk(item):
                            if hasattr(child, 'lineno') and child.lineno > end_line:
                                end_line = child.lineno
                        
                        method_lines = end_line - item.lineno + 1
                            
                        functions.append({
                            'name': item.name,
                            'line': item.lineno,
                            'type': 'method',
                            'class': node.name,
                            'size': method_lines
                        })
                        
    except Exception as e:
        pass
        
    return functions

def find_function_calls_detailed(file_path):
    calls = defaultdict(int)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Function calls
        pattern1 = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches1 = re.findall(pattern1, content)
        for match in matches1:
            calls[match] += 1
        
        # Method calls
        pattern2 = r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches2 = re.findall(pattern2, content)
        for match in matches2:
            calls[match] += 1
        
        # Imports
        pattern3 = r'from\s+[\w.]+\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches3 = re.findall(pattern3, content)
        for match in matches3:
            calls[match] += 1
        
        # Remove reserved words
        reserved = {'if', 'for', 'while', 'def', 'class', 'return', 'import', 'from', 'as', 'with', 'try', 'except', 'finally', 'lambda', 'yield', 'async', 'await', 'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'max', 'min', 'sum', 'all', 'any', 'sorted', 'reversed', 'open', 'super', 'isinstance', 'hasattr', 'getattr', 'setattr', 'type'}
        for word in reserved:
            if word in calls:
                del calls[word]
        
    except Exception as e:
        pass
    
    return calls

# Find Python files
py_files = []
src_path = os.path.join(os.getcwd(), 'src')
for root, dirs, files in os.walk(src_path):
    for file in files:
        if file.endswith('.py'):
            py_files.append(os.path.join(root, file))

# Extract defined functions
for file_path in py_files:
    functions = extract_functions_from_file(file_path)
    for func in functions:
        func_key = f'{func["name"]}_{func["type"]}_{func["class"] or "None"}'
        defined_functions[func_key] = {
            'name': func['name'],
            'file': file_path,
            'line': func['line'],
            'type': func['type'],
            'class': func['class'],
            'size': func['size']
        }

# Extract function calls with counts
for file_path in py_files:
    calls = find_function_calls_detailed(file_path)
    for func_name, count in calls.items():
        called_functions[func_name] += count

# Analyze usage patterns
unused_functions = []
rarely_used = []
single_use = []
well_used = []

for func_key, func_info in defined_functions.items():
    func_name = func_info['name']
    usage_count = called_functions.get(func_name, 0)
    
    # Skip known entry points and overrides
    if func_name in ['main', '__init__']:
        continue
    
    if any(pattern in func_name for pattern in ['handle_', 'do_', 'on_']):
        continue
    
    if func_info['type'] == 'method' and func_name in ['calculate', 'validate_data', 'get_required_columns', 'run_monitoring', 'is_active']:
        continue
    
    func_info['usage_count'] = usage_count
    
    if usage_count == 0:
        unused_functions.append(func_info)
    elif usage_count == 1:
        single_use.append(func_info)
    elif usage_count <= 3:
        rarely_used.append(func_info)
    else:
        well_used.append(func_info)

# Sort by various criteria
unused_functions.sort(key=lambda x: x['size'], reverse=True)
rarely_used.sort(key=lambda x: x['size'], reverse=True)
single_use.sort(key=lambda x: x['size'], reverse=True)

print("ANALISE DETALHADA DE FUNCOES NAO UTILIZADAS")
print("=" * 60)

print(f"\nESTATISTICAS GERAIS:")
print(f"Total de funcoes definidas: {len(defined_functions)}")
print(f"Total de chamadas unicas: {len(called_functions)}")
print(f"Funcoes nao utilizadas: {len(unused_functions)}")
print(f"Funcoes com uso unico: {len(single_use)}")
print(f"Funcoes raramente usadas (2-3x): {len(rarely_used)}")
print(f"Funcoes bem utilizadas (4+x): {len(well_used)}")

print(f"\nFUNCOES COMPLETAMENTE NAO UTILIZADAS:")
if not unused_functions:
    print("Nenhuma funcao completamente nao utilizada encontrada!")
else:
    for func in unused_functions[:10]:
        rel_path = func['file'].replace(os.getcwd(), '').replace('\\', '/')
        print(f"  {rel_path}:{func['line']} - {func['name']} ({func['size']} linhas)")

print(f"\nFUNCOES COM USO UNICO (candidatas a refatoracao):")
for func in single_use[:10]:
    rel_path = func['file'].replace(os.getcwd(), '').replace('\\', '/')
    func_type = f"({func['class']}.{func['name']})" if func['class'] else f"({func['name']})"
    print(f"  {rel_path}:{func['line']} - {func_type} ({func['size']} linhas)")

print(f"\nFUNCOES RARAMENTE USADAS (2-3 chamadas):")
for func in rarely_used[:10]:
    rel_path = func['file'].replace(os.getcwd(), '').replace('\\', '/')
    func_type = f"({func['class']}.{func['name']})" if func['class'] else f"({func['name']})"
    usage = func['usage_count']
    print(f"  {rel_path}:{func['line']} - {func_type} ({func['size']} linhas, {usage}x)")

# Find large functions
large_functions = [f for f in defined_functions.values() if f['size'] > 50]
large_functions.sort(key=lambda x: x['size'], reverse=True)

print(f"\nFUNCOES GRANDES (>50 linhas) - Candidatas a divisao:")
for func in large_functions[:10]:
    rel_path = func['file'].replace(os.getcwd(), '').replace('\\', '/')
    func_type = f"({func['class']}.{func['name']})" if func['class'] else f"({func['name']})"
    usage = called_functions.get(func['name'], 0)
    print(f"  {rel_path}:{func['line']} - {func_type} ({func['size']} linhas, {usage}x)")

# Calculate potential cleanup impact
total_unused_lines = sum(f['size'] for f in unused_functions)
total_single_use_lines = sum(f['size'] for f in single_use)
total_rarely_used_lines = sum(f['size'] for f in rarely_used)

print(f"\nIMPACTO POTENCIAL DE LIMPEZA:")
print(f"Linhas em funcoes nao utilizadas: {total_unused_lines}")
print(f"Linhas em funcoes de uso unico: {total_single_use_lines}")
print(f"Linhas em funcoes raramente usadas: {total_rarely_used_lines}")
print(f"Total de linhas candidatas a revisao: {total_unused_lines + total_single_use_lines + total_rarely_used_lines}")