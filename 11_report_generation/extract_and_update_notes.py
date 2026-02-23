#!/usr/bin/env python3
"""
Extract process and results from notebooks and update notes.md files
"""
import json
import os
from pathlib import Path
import re

def extract_process_from_code(source_code):
    """Extract process steps from code"""
    processes = []
    lines = source_code.split('\n')
    
    current_step = []
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines and imports at start
        if not line_stripped or line_stripped.startswith('import ') or line_stripped.startswith('from '):
            continue
        
        # Look for key operations
        if any(op in line_stripped for op in ['save', 'to_csv', 'to_parquet', 'to_png', 'plt.savefig', 'generate', 'create', 'calculate', 'analyze', 'detect', 'filter', 'group', 'merge']):
            # Extract the operation
            if '=' in line_stripped:
                var = line_stripped.split('=')[0].strip()
                if len(var) < 50:
                    current_step.append(f"{var}")
            elif '(' in line_stripped:
                # Extract function call
                match = re.search(r'(\w+)\(', line_stripped)
                if match:
                    current_step.append(match.group(1))
        
        # Look for print statements that describe what's happening
        if 'print(' in line_stripped and any(word in line_stripped for word in ['saving', 'generating', 'creating', 'calculating', 'analyzing']):
            match = re.search(r'print\(["\']([^"\']+)["\']', line_stripped)
            if match:
                current_step.append(match.group(1))
    
    if current_step:
        processes.append('; '.join(set(current_step[:5])))  # Remove duplicates, limit
    
    return processes

def extract_results_from_outputs(cell):
    """Extract results from cell outputs"""
    results = []
    if 'outputs' not in cell:
        return results
    
    for output in cell['outputs']:
        if output.get('output_type') == 'stream':
            text = ''.join(output.get('text', []))
            if text.strip():
                # Extract key statistics
                lines = text.split('\n')
                for line in lines[:10]:  # First 10 lines
                    if any(keyword in line.lower() for keyword in ['total', 'count', 'rows', 'found', 'detected', 'saved', 'generated', 'success']):
                        results.append(line.strip())
        elif output.get('output_type') == 'execute_result':
            if 'data' in output:
                if 'text/plain' in output['data']:
                    text = ''.join(output['data']['text/plain'])
                    # Get summary stats
                    lines = text.split('\n')[:5]
                    results.extend([l.strip() for l in lines if l.strip()])
    
    return results[:10]  # Limit results

def analyze_notebook(notebook_path):
    """Analyze notebook to extract process and results"""
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    all_processes = []
    all_results = []
    
    code_cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code']
    
    for i, cell in enumerate(code_cells):
        source = ''.join(cell.get('source', []))
        if not source.strip():
            continue
        
        # Extract process
        processes = extract_process_from_code(source)
        if processes:
            all_processes.extend([f"Cell {i+1}: {p}" for p in processes])
        
        # Extract results
        results = extract_results_from_outputs(cell)
        if results:
            all_results.extend(results)
    
    return all_processes, all_results

def get_output_files(folder_path):
    """Get list of output files"""
    outputs = []
    outputs_dir = os.path.join(folder_path, 'outputs')
    if os.path.exists(outputs_dir):
        for root, dirs, files in os.walk(outputs_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), folder_path)
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                outputs.append((rel_path, size))
    return outputs

def update_notes(notes_path, notebook_name, processes, results, output_files):
    """Update notes.md with process and results"""
    # Clean notebook name for title
    title = notebook_name.replace('_', ' ').replace('.ipynb', '').title()
    
    content = f"# {title}\n\n"
    
    content += "## Process\n\n"
    if processes:
        for process in processes[:15]:  # Limit to 15 process steps
            content += f"- {process}\n"
    else:
        content += "- Process steps will be documented after execution\n"
    
    content += "\n## Results\n\n"
    
    if results:
        content += "### Execution Outputs\n\n"
        for i, result in enumerate(results[:15], 1):  # Limit to 15 results
            if len(result) > 200:
                result = result[:200] + "..."
            content += f"{i}. {result}\n"
        content += "\n"
    
    if output_files:
        content += "### Generated Files\n\n"
        total_size = 0
        for file_path, size in output_files:
            size_mb = size / (1024 * 1024)
            if size_mb > 1:
                content += f"- `{file_path}` ({size_mb:.2f} MB)\n"
            else:
                content += f"- `{file_path}` ({size / 1024:.2f} KB)\n"
            total_size += size
        content += f"\n**Total output size:** {total_size / (1024 * 1024):.2f} MB\n\n"
    else:
        content += "### Generated Files\n\n"
        content += "- No output files found. Run the notebook to generate outputs.\n\n"
    
    with open(notes_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {notes_path}")

def main():
    notebooks_dir = Path(__file__).parent
    
    # Find all notebook folders
    notebook_folders = [d for d in notebooks_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    print(f"Found {len(notebook_folders)} notebook folders\n")
    
    for folder in sorted(notebook_folders):
        notebook_files = list(folder.glob("*.ipynb"))
        if not notebook_files:
            continue
        
        notebook_path = notebook_files[0]  # Take first notebook
        notes_path = folder / "notes.md"
        
        print(f"\n{'='*60}")
        print(f"Processing: {folder.name}")
        print(f"Notebook: {notebook_path.name}")
        print(f"{'='*60}")
        
        # Analyze notebook
        processes, results = analyze_notebook(str(notebook_path))
        print(f"  Found {len(processes)} process steps")
        print(f"  Found {len(results)} result outputs")
        
        # Get output files
        output_files = get_output_files(str(folder))
        print(f"  Found {len(output_files)} output files")
        
        # Update notes
        update_notes(str(notes_path), notebook_path.name, processes, results, output_files)

if __name__ == "__main__":
    main()
