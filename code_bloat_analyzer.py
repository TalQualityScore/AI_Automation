# code_bloat_analyzer.py
"""
AI Automation Suite - Code Bloat Analyzer
Identifies oversized files, complex functions, and suggests refactoring opportunities
"""

import os
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class FileMetrics:
    """Metrics for a single file"""
    path: str
    lines_of_code: int
    total_lines: int
    num_functions: int
    num_classes: int
    num_imports: int
    largest_function: Tuple[str, int]  # (name, lines)
    largest_class: Tuple[str, int]  # (name, lines)
    complexity_score: int
    duplicate_code_blocks: int
    suggested_splits: List[str]

@dataclass
class FunctionMetrics:
    """Metrics for a single function"""
    name: str
    lines: int
    complexity: int
    num_parameters: int
    num_returns: int
    has_nested_functions: bool
    calls_other_functions: List[str]

@dataclass
class RefactoringRecommendation:
    """Refactoring recommendation for a file"""
    file_path: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    issues: List[str]
    suggested_modules: List[Dict[str, List[str]]]  # Module name -> functions/classes
    estimated_files_after_split: int

class CodeBloatAnalyzer:
    """Analyzes Python code for bloat and suggests refactoring"""
    
    # Thresholds for detection
    THRESHOLDS = {
        'max_file_lines': 500,           # Files over 500 lines are considered large
        'critical_file_lines': 1000,     # Files over 1000 lines are critical
        'max_function_lines': 50,        # Functions over 50 lines are large
        'critical_function_lines': 100,  # Functions over 100 lines are critical
        'max_class_lines': 200,          # Classes over 200 lines are large
        'max_complexity': 10,             # Cyclomatic complexity threshold
        'max_parameters': 5,              # Max parameters for a function
        'max_imports': 20,                # Too many imports indicate doing too much
        'min_duplicate_lines': 10         # Minimum lines to consider as duplicate
    }
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.file_metrics: Dict[str, FileMetrics] = {}
        self.function_metrics: Dict[str, List[FunctionMetrics]] = defaultdict(list)
        self.recommendations: List[RefactoringRecommendation] = []
        
    def analyze_project(self, exclude_dirs: List[str] = None) -> Dict:
        """Analyze entire project for code bloat"""
        if exclude_dirs is None:
            exclude_dirs = ['venv', 'env', '__pycache__', '.git', 'node_modules', 'dist', 'build']
        
        print("=" * 80)
        print("CODE BLOAT ANALYZER - AI AUTOMATION SUITE")
        print("=" * 80)
        print(f"\n📂 Analyzing project: {self.project_root}")
        
        # Find all Python files
        python_files = self._find_python_files(exclude_dirs)
        print(f"📊 Found {len(python_files)} Python files to analyze\n")
        
        # Analyze each file
        for file_path in python_files:
            self._analyze_file(file_path)
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Generate report
        return self._generate_report()
    
    def _find_python_files(self, exclude_dirs: List[str]) -> List[Path]:
        """Find all Python files in project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        return python_files
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Count basic metrics
            total_lines = len(lines)
            code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
            
            # Parse AST for detailed analysis
            try:
                tree = ast.parse(content)
                
                # Extract detailed metrics
                num_functions = 0
                num_classes = 0
                num_imports = 0
                largest_function = ("", 0)
                largest_class = ("", 0)
                complexity_score = 0
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                        num_imports += 1
                    elif isinstance(node, ast.FunctionDef):
                        num_functions += 1
                        func_lines = self._count_node_lines(node, lines)
                        if func_lines > largest_function[1]:
                            largest_function = (node.name, func_lines)
                        
                        # Analyze function complexity
                        func_metrics = self._analyze_function(node, lines)
                        self.function_metrics[str(file_path)].append(func_metrics)
                        complexity_score += func_metrics.complexity
                        
                    elif isinstance(node, ast.ClassDef):
                        num_classes += 1
                        class_lines = self._count_node_lines(node, lines)
                        if class_lines > largest_class[1]:
                            largest_class = (node.name, class_lines)
                
                # Find duplicate code blocks
                duplicate_blocks = self._find_duplicate_blocks(lines)
                
                # Generate split suggestions
                suggested_splits = self._suggest_splits(
                    tree, total_lines, num_functions, num_classes, complexity_score
                )
                
                # Store metrics
                self.file_metrics[str(file_path)] = FileMetrics(
                    path=str(file_path),
                    lines_of_code=code_lines,
                    total_lines=total_lines,
                    num_functions=num_functions,
                    num_classes=num_classes,
                    num_imports=num_imports,
                    largest_function=largest_function,
                    largest_class=largest_class,
                    complexity_score=complexity_score,
                    duplicate_code_blocks=len(duplicate_blocks),
                    suggested_splits=suggested_splits
                )
                
            except SyntaxError as e:
                print(f"⚠️ Syntax error in {file_path}: {e}")
                
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
    
    def _count_node_lines(self, node: ast.AST, lines: List[str]) -> int:
        """Count lines for an AST node"""
        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _analyze_function(self, node: ast.FunctionDef, lines: List[str]) -> FunctionMetrics:
        """Analyze a function for complexity"""
        complexity = self._calculate_complexity(node)
        num_returns = sum(1 for n in ast.walk(node) if isinstance(n, ast.Return))
        has_nested = any(isinstance(n, ast.FunctionDef) for n in node.body)
        
        # Find function calls
        calls = []
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name):
                    calls.append(n.func.id)
                elif isinstance(n.func, ast.Attribute):
                    calls.append(n.func.attr)
        
        return FunctionMetrics(
            name=node.name,
            lines=self._count_node_lines(node, lines),
            complexity=complexity,
            num_parameters=len(node.args.args),
            num_returns=num_returns,
            has_nested_functions=has_nested,
            calls_other_functions=calls[:10]  # Limit to first 10
        )
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a node"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _find_duplicate_blocks(self, lines: List[str]) -> List[Tuple[int, int, int]]:
        """Find duplicate code blocks (simple implementation)"""
        duplicates = []
        block_size = self.THRESHOLDS['min_duplicate_lines']
        
        # Create hash of blocks
        blocks = {}
        for i in range(len(lines) - block_size + 1):
            block = '\n'.join(lines[i:i + block_size])
            block_hash = hash(block)
            
            if block_hash in blocks:
                duplicates.append((blocks[block_hash], i, block_size))
            else:
                blocks[block_hash] = i
        
        return duplicates
    
    def _suggest_splits(self, tree: ast.AST, total_lines: int, 
                       num_functions: int, num_classes: int, 
                       complexity: int) -> List[str]:
        """Suggest how to split a large file"""
        suggestions = []
        
        if total_lines > self.THRESHOLDS['critical_file_lines']:
            suggestions.append("CRITICAL: File is over 1000 lines - urgent refactoring needed")
        elif total_lines > self.THRESHOLDS['max_file_lines']:
            suggestions.append("File is over 500 lines - consider splitting")
        
        # Analyze imports for grouping
        import_groups = self._analyze_import_groups(tree)
        if len(import_groups) > 3:
            suggestions.append(f"Multiple import groups detected ({len(import_groups)}) - consider splitting by domain")
        
        # Check for mixed responsibilities
        has_ui = any('ui' in str(n).lower() or 'dialog' in str(n).lower() 
                     for n in ast.walk(tree) if isinstance(n, ast.Name))
        has_api = any('api' in str(n).lower() or 'client' in str(n).lower() 
                     for n in ast.walk(tree) if isinstance(n, ast.Name))
        has_db = any('database' in str(n).lower() or 'model' in str(n).lower() 
                    for n in ast.walk(tree) if isinstance(n, ast.Name))
        
        responsibilities = sum([has_ui, has_api, has_db])
        if responsibilities > 1:
            suggestions.append("Mixed responsibilities detected - separate UI, API, and data layers")
        
        # Check class size
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(class_methods) > 10:
                    suggestions.append(f"Class '{node.name}' has {len(class_methods)} methods - consider splitting")
        
        return suggestions
    
    def _analyze_import_groups(self, tree: ast.AST) -> Dict[str, List[str]]:
        """Group imports by type"""
        groups = defaultdict(list)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    groups['standard'].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module.startswith('.'):
                        groups['relative'].append(node.module)
                    elif any(node.module.startswith(pkg) for pkg in ['tkinter', 'flask', 'django']):
                        groups['framework'].append(node.module)
                    else:
                        groups['third_party'].append(node.module)
        
        return dict(groups)
    
    def _generate_recommendations(self) -> None:
        """Generate refactoring recommendations"""
        for file_path, metrics in self.file_metrics.items():
            issues = []
            severity = 'low'
            suggested_modules = []
            
            # Check file size
            if metrics.total_lines > self.THRESHOLDS['critical_file_lines']:
                severity = 'critical'
                issues.append(f"File has {metrics.total_lines} lines (critical threshold: {self.THRESHOLDS['critical_file_lines']})")
            elif metrics.total_lines > self.THRESHOLDS['max_file_lines']:
                severity = 'high'
                issues.append(f"File has {metrics.total_lines} lines (threshold: {self.THRESHOLDS['max_file_lines']})")
            
            # Check function size
            if metrics.largest_function[1] > self.THRESHOLDS['critical_function_lines']:
                if severity != 'critical':
                    severity = 'high'
                issues.append(f"Function '{metrics.largest_function[0]}' has {metrics.largest_function[1]} lines")
            
            # Check complexity
            if metrics.complexity_score > self.THRESHOLDS['max_complexity'] * metrics.num_functions:
                if severity == 'low':
                    severity = 'medium'
                issues.append(f"High overall complexity score: {metrics.complexity_score}")
            
            # Check imports
            if metrics.num_imports > self.THRESHOLDS['max_imports']:
                if severity == 'low':
                    severity = 'medium'
                issues.append(f"Too many imports: {metrics.num_imports}")
            
            # Check duplicate code
            if metrics.duplicate_code_blocks > 3:
                issues.append(f"Found {metrics.duplicate_code_blocks} duplicate code blocks")
            
            # Generate module suggestions
            if metrics.num_functions > 10:
                # Group related functions
                func_groups = self._group_related_functions(file_path)
                for group_name, functions in func_groups.items():
                    if len(functions) > 2:
                        suggested_modules.append({
                            group_name: functions
                        })
            
            if issues:
                self.recommendations.append(RefactoringRecommendation(
                    file_path=file_path,
                    severity=severity,
                    issues=issues,
                    suggested_modules=suggested_modules,
                    estimated_files_after_split=max(1, len(suggested_modules))
                ))
    
    def _group_related_functions(self, file_path: str) -> Dict[str, List[str]]:
        """Group related functions based on naming and usage patterns"""
        groups = defaultdict(list)
        
        if file_path in self.function_metrics:
            for func in self.function_metrics[file_path]:
                # Group by prefix
                if '_' in func.name:
                    prefix = func.name.split('_')[0]
                    groups[f"{prefix}_module"].append(func.name)
                # Group by common patterns
                elif 'process' in func.name.lower():
                    groups['processing_module'].append(func.name)
                elif 'validate' in func.name.lower():
                    groups['validation_module'].append(func.name)
                elif 'ui' in func.name.lower() or 'dialog' in func.name.lower():
                    groups['ui_module'].append(func.name)
                elif 'api' in func.name.lower() or 'client' in func.name.lower():
                    groups['api_module'].append(func.name)
                else:
                    groups['utils_module'].append(func.name)
        
        return dict(groups)
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        # Sort recommendations by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        self.recommendations.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        # Calculate statistics
        total_files = len(self.file_metrics)
        total_lines = sum(m.total_lines for m in self.file_metrics.values())
        bloated_files = [f for f, m in self.file_metrics.items() 
                        if m.total_lines > self.THRESHOLDS['max_file_lines']]
        critical_files = [f for f, m in self.file_metrics.items() 
                         if m.total_lines > self.THRESHOLDS['critical_file_lines']]
        
        # Print report
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        print(f"\n📊 OVERALL STATISTICS:")
        print(f"   Total files analyzed: {total_files}")
        print(f"   Total lines of code: {total_lines:,}")
        print(f"   Average file size: {total_lines // total_files if total_files else 0} lines")
        print(f"   Bloated files (>500 lines): {len(bloated_files)}")
        print(f"   Critical files (>1000 lines): {len(critical_files)}")
        
        # Top 10 largest files
        print(f"\n📈 TOP 10 LARGEST FILES:")
        sorted_files = sorted(self.file_metrics.items(), 
                            key=lambda x: x[1].total_lines, reverse=True)[:10]
        
        for i, (path, metrics) in enumerate(sorted_files, 1):
            rel_path = Path(path).relative_to(self.project_root)
            print(f"   {i:2}. {rel_path}")
            print(f"       Lines: {metrics.total_lines:,} | Functions: {metrics.num_functions} | Classes: {metrics.num_classes}")
            if metrics.largest_function[1] > 0:
                print(f"       Largest function: {metrics.largest_function[0]} ({metrics.largest_function[1]} lines)")
        
        # Critical recommendations
        print(f"\n🚨 CRITICAL REFACTORING NEEDED:")
        critical_recs = [r for r in self.recommendations if r.severity == 'critical']
        
        if critical_recs:
            for rec in critical_recs[:5]:
                rel_path = Path(rec.file_path).relative_to(self.project_root)
                print(f"\n   📁 {rel_path}")
                for issue in rec.issues:
                    print(f"      ❌ {issue}")
                if rec.suggested_modules:
                    print(f"      💡 Suggested split into {len(rec.suggested_modules)} modules:")
                    for module in rec.suggested_modules[:3]:
                        for name, funcs in module.items():
                            print(f"         - {name}: {len(funcs)} functions")
        else:
            print("   ✅ No critical issues found!")
        
        # Refactoring suggestions
        print(f"\n💡 REFACTORING SUGGESTIONS:")
        
        suggestions = defaultdict(list)
        for rec in self.recommendations:
            for issue in rec.issues:
                if 'lines' in issue:
                    suggestions['size'].append(Path(rec.file_path).name)
                elif 'complexity' in issue:
                    suggestions['complexity'].append(Path(rec.file_path).name)
                elif 'imports' in issue:
                    suggestions['imports'].append(Path(rec.file_path).name)
                elif 'duplicate' in issue:
                    suggestions['duplicates'].append(Path(rec.file_path).name)
        
        for category, files in suggestions.items():
            if files:
                print(f"\n   {category.upper()} ISSUES:")
                for file in set(files[:5]):
                    print(f"      - {file}")
        
        # Save detailed report
        self._save_detailed_report()
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'bloated_files': bloated_files,
            'critical_files': critical_files,
            'recommendations': len(self.recommendations),
            'critical_recommendations': len(critical_recs)
        }
    
    def _save_detailed_report(self) -> None:
        """Save detailed report to file"""
        report_path = self.project_root / "code_bloat_report.json"
        
        report_data = {
            'summary': {
                'total_files': len(self.file_metrics),
                'total_lines': sum(m.total_lines for m in self.file_metrics.values()),
                'critical_files': len([f for f, m in self.file_metrics.items() 
                                     if m.total_lines > self.THRESHOLDS['critical_file_lines']])
            },
            'thresholds': self.THRESHOLDS,
            'files': [],
            'recommendations': []
        }
        
        # Add file metrics
        for path, metrics in self.file_metrics.items():
            report_data['files'].append({
                'path': str(Path(path).relative_to(self.project_root)),
                'lines': metrics.total_lines,
                'functions': metrics.num_functions,
                'classes': metrics.num_classes,
                'complexity': metrics.complexity_score,
                'largest_function': {
                    'name': metrics.largest_function[0],
                    'lines': metrics.largest_function[1]
                }
            })
        
        # Add recommendations
        for rec in self.recommendations:
            report_data['recommendations'].append({
                'file': str(Path(rec.file_path).relative_to(self.project_root)),
                'severity': rec.severity,
                'issues': rec.issues,
                'suggested_splits': rec.estimated_files_after_split
            })
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")

def main():
    """Run the code bloat analyzer"""
    import sys
    
    # Check if we're in the right directory
    if not os.path.exists("local_automation.py"):
        print("❌ ERROR: Must run from project root directory")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    print("🔍 Starting Code Bloat Analysis...")
    print("This will identify oversized files and suggest refactoring.\n")
    
    analyzer = CodeBloatAnalyzer(".")
    results = analyzer.analyze_project()
    
    print("\n" + "=" * 80)
    print("RECOMMENDED ACTIONS")
    print("=" * 80)
    
    if results['critical_files']:
        print("\n🚨 IMMEDIATE ACTION REQUIRED:")
        print("   1. Split critical files (>1000 lines) into smaller modules")
        print("   2. Extract related functions into separate files")
        print("   3. Create proper module structure with __init__.py files")
    
    if results['bloated_files']:
        print("\n⚠️ HIGH PRIORITY:")
        print("   1. Refactor files over 500 lines")
        print("   2. Extract UI components into separate files")
        print("   3. Separate business logic from presentation")
    
    print("\n✅ BEST PRACTICES:")
    print("   1. Keep files under 500 lines")
    print("   2. Keep functions under 50 lines")
    print("   3. Keep classes under 200 lines")
    print("   4. Maintain single responsibility per file")
    print("   5. Use meaningful module names")
    
    print("\n🎯 Next Steps:")
    print("   1. Review code_bloat_report.json for detailed analysis")
    print("   2. Start with critical files first")
    print("   3. Create a refactoring plan")
    print("   4. Test after each refactoring")
    
    return results

if __name__ == "__main__":
    main()