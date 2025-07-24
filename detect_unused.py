import ast
import os
import re

defined_functions = {}
called_functions = set()

def extract_functions_from_file(file_path):
    functions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('__') and node.name.endswith('__') and node.name != '__init__':
                    continue
                    
                functions.append({
                    'name': node.name,
                    'line': node.lineno,
                    'type': 'function',
                    'class': None
                })
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        if item.name.startswith('__') and item.name.endswith('__') and item.name != '__init__':
                            continue
                            
                        functions.append({
                            'name': item.name,
                            'line': item.lineno,
                            'type': 'method',
                            'class': node.name
                        })
                        
    except Exception as e:
        pass
        
    return functions

def find_function_calls(file_path):
    calls = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern1 = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches1 = re.findall(pattern1, content)
        calls.update(matches1)
        
        pattern2 = r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches2 = re.findall(pattern2, content)
        calls.update(matches2)
        
        pattern3 = r'from\s+[\w.]+\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        matches3 = re.findall(pattern3, content)
        calls.update(matches3)
        
        reserved = {'if', 'for', 'while', 'def', 'class', 'return', 'import', 'from', 'as', 'with', 'try', 'except', 'finally', 'lambda', 'yield', 'async', 'await', 'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'max', 'min', 'sum', 'all', 'any', 'sorted', 'reversed', 'open', 'super', 'isinstance', 'hasattr', 'getattr', 'setattr', 'type'}
        calls = calls - reserved
        
    except Exception as e:
        pass
    
    return calls

# Encontrar arquivos Python
py_files = []
src_path = os.path.join(os.getcwd(), 'src')
for root, dirs, files in os.walk(src_path):
    for file in files:
        if file.endswith('.py'):
            py_files.append(os.path.join(root, file))

# Extrair funções definidas
for file_path in py_files:
    functions = extract_functions_from_file(file_path)
    for func in functions:
        func_key = f'{func["name"]}_{func["type"]}_{func["class"] or "None"}'
        defined_functions[func_key] = {
            'name': func['name'],
            'file': file_path,
            'line': func['line'],
            'type': func['type'],
            'class': func['class']
        }

# Extrair chamadas de função
for file_path in py_files:
    calls = find_function_calls(file_path)
    called_functions.update(calls)

# Identificar funções não utilizadas
unused_functions = []
potentially_unused = []

for func_key, func_info in defined_functions.items():
    func_name = func_info['name']
    
    # Pular entry points conhecidos
    if func_name in ['main', '__init__', 'run_monitoring', 'load_pool_data']:
        continue
    
    # Pular callbacks e handlers
    if any(pattern in func_name for pattern in ['handle_', 'do_', 'on_', 'callback', 'handler']):
        continue
    
    # Verificar se a função é chamada
    if func_name not in called_functions:
        if func_info['type'] == 'method':
            # Para métodos, verificar se é override de classe base
            if func_name in ['calculate', 'validate_data', 'get_required_columns', 'run_monitoring', 'is_active']:
                continue  # Estes são overrides de BaseMonitor
        
        # Se chegou até aqui, pode ser código morto
        if func_name.startswith('_'):
            potentially_unused.append(func_info)
        else:
            unused_functions.append(func_info)

print(f'SUMMARY:')
print(f'Total functions defined: {len(defined_functions)}')
print(f'Total function calls found: {len(called_functions)}')
print(f'Potentially unused functions: {len(unused_functions)}')
print(f'Suspicious private functions: {len(potentially_unused)}')

print(f'\nUNUSED_FUNCTIONS:')
for func in unused_functions:
    print(f'UNUSED:{func["file"]}:{func["line"]}:{func["name"]}:{func["type"]}:{func["class"] or "None"}')

print(f'\nSUSPICIOUS_PRIVATE:')
for func in potentially_unused[:15]:
    print(f'SUSPICIOUS:{func["file"]}:{func["line"]}:{func["name"]}:{func["type"]}:{func["class"] or "None"}')