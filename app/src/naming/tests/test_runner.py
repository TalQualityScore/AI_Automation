# app/src/naming/tests/test_runner.py
"""
Test Runner for the Naming Module

Runs all tests for the naming system components and provides
comprehensive reporting of test results.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from test_version_extraction import TestVersionExtraction, TestVersionExtractionIntegration
from test_project_parsing import TestProjectParsing, TestProjectParsingIntegration  
from test_name_generation import TestNameGeneration, TestNameGenerationIntegration

class NamingTestRunner:
    """Comprehensive test runner for the naming system"""
    
    def __init__(self):
        self.test_suites = {
            'Version Extraction': [TestVersionExtraction, TestVersionExtractionIntegration],
            'Project Parsing': [TestProjectParsing, TestProjectParsingIntegration],
            'Name Generation': [TestNameGeneration, TestNameGenerationIntegration]
        }
        
        self.results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_time = 0
    
    def run_all_tests(self, verbosity=2):
        """Run all naming system tests"""
        print("🚀 NAMING SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        print(f"Running tests for {len(self.test_suites)} module categories...")
        print()
        
        start_time = time.time()
        
        for category, test_classes in self.test_suites.items():
            print(f"📋 Testing: {category}")
            print("-" * 50)
            
            category_results = self._run_category_tests(test_classes, verbosity)
            self.results[category] = category_results
            
            # Update totals
            self.total_tests += category_results['tests_run']
            self.total_failures += category_results['failures'] 
            self.total_errors += category_results['errors']
            
            print()
        
        self.total_time = time.time() - start_time
        
        # Print comprehensive summary
        self._print_final_summary()
        
        return self._get_overall_success()
    
    def _run_category_tests(self, test_classes, verbosity):
        """Run tests for a specific category"""
        suite = unittest.TestSuite()
        
        # Add all test classes to the suite
        for test_class in test_classes:
            suite.addTest(unittest.makeSuite(test_class))
        
        # Capture output
        output_stream = StringIO()
        runner = unittest.TextTestRunner(stream=output_stream, verbosity=verbosity)
        
        # Run the tests
        result = runner.run(suite)
        
        # Process results
        category_results = {
            'tests_run': result.testsRun,
            'failures': len(result.failures),
            'errors': len(result.errors),
            'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / max(result.testsRun, 1),
            'output': output_stream.getvalue(),
            'failure_details': result.failures,
            'error_details': result.errors
        }
        
        # Print category summary
        self._print_category_summary(category_results)
        
        return category_results
    
    def _print_category_summary(self, results):
        """Print summary for a test category"""
        tests_run = results['tests_run']
        failures = results['failures']
        errors = results['errors']
        success_rate = results['success_rate']
        
        if failures == 0 and errors == 0:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        
        print(f"   {status} - {tests_run} tests, {success_rate:.1%} success rate")
        
        if failures > 0:
            print(f"   ⚠️  {failures} failures")
        
        if errors > 0:
            print(f"   🚨 {errors} errors")
    
    def _print_final_summary(self):
        """Print comprehensive final summary"""
        print("📊 FINAL TEST RESULTS")
        print("=" * 70)
        
        # Overall statistics
        overall_success_rate = (self.total_tests - self.total_failures - self.total_errors) / max(self.total_tests, 1)
        
        print(f"🎯 Overall Results:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.total_tests - self.total_failures - self.total_errors}")
        print(f"   Failed: {self.total_failures}")
        print(f"   Errors: {self.total_errors}")
        print(f"   Success Rate: {overall_success_rate:.1%}")
        print(f"   Total Time: {self.total_time:.2f} seconds")
        print()
        
        # Category breakdown
        print(f"📋 Category Breakdown:")
        for category, results in self.results.items():
            success_rate = results['success_rate']
            status_icon = "✅" if results['failures'] == 0 and results['errors'] == 0 else "❌"
            print(f"   {status_icon} {category}: {results['tests_run']} tests, {success_rate:.1%} success")
        print()
        
        # Detailed failure/error reporting
        if self.total_failures > 0 or self.total_errors > 0:
            print("🔍 DETAILED FAILURE/ERROR REPORT:")
            print("-" * 50)
            
            for category, results in self.results.items():
                if results['failures'] or results['errors']:
                    print(f"\n❌ {category} Issues:")
                    
                    for test, traceback in results['failure_details']:
                        print(f"   FAILURE: {test}")
                        # Print first line of traceback for brevity
                        first_line = traceback.split('\n')[0] if traceback else "No details"
                        print(f"   └─ {first_line}")
                    
                    for test, traceback in results['error_details']:
                        print(f"   ERROR: {test}")
                        first_line = traceback.split('\n')[0] if traceback else "No details"
                        print(f"   └─ {first_line}")
        
        # Critical test highlights
        self._print_critical_test_highlights()
    
    def _print_critical_test_highlights(self):
        """Print highlights for critical tests (your specific issues)"""
        print("🎯 CRITICAL TEST HIGHLIGHTS:")
        print("-" * 50)
        
        critical_tests = [
            "Version letter extraction from _250416D format",
            "Account detection not overriding TR with BC3", 
            "Project name flow through processing pipeline",
            "Version letter 'D' not 'S' in output names"
        ]
        
        print("These tests specifically address your reported issues:")
        for test in critical_tests:
            print(f"   🔍 {test}")
        
        print()
        print("If these tests pass, your original issues should be resolved!")
    
    def _get_overall_success(self):
        """Get overall success status"""
        return self.total_failures == 0 and self.total_errors == 0
    
    def run_specific_category(self, category_name, verbosity=2):
        """Run tests for a specific category only"""
        if category_name not in self.test_suites:
            print(f"❌ Unknown category: {category_name}")
            print(f"Available categories: {list(self.test_suites.keys())}")
            return False
        
        print(f"🚀 RUNNING SPECIFIC CATEGORY: {category_name}")
        print("=" * 50)
        
        test_classes = self.test_suites[category_name]
        results = self._run_category_tests(test_classes, verbosity)
        
        return results['failures'] == 0 and results['errors'] == 0
    
    def run_critical_tests_only(self, verbosity=2):
        """Run only the most critical tests for your specific issues"""
        print("🎯 RUNNING CRITICAL TESTS ONLY")
        print("=" * 50)
        print("These tests focus on your specific reported issues...")
        print()
        
        # Create a suite with only critical tests
        suite = unittest.TestSuite()
        
        # Add specific critical test methods
        critical_test_methods = [
            # Version extraction critical tests
            TestVersionExtraction('test_250416_format_extraction'),
            TestVersionExtractionIntegration('test_your_specific_problem_files'),
            
            # Name generation critical tests  
            TestNameGeneration('test_output_name_generation_extract_version'),
            TestNameGenerationIntegration('test_your_specific_problem_scenario'),
        ]
        
        for test_method in critical_test_methods:
            suite.addTest(test_method)
        
        # Run critical tests
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        # Print critical test summary
        if result.wasSuccessful():
            print("\n✅ ALL CRITICAL TESTS PASSED!")
            print("🎉 Your original issues should now be resolved!")
        else:
            print(f"\n❌ CRITICAL TESTS FAILED!")
            print(f"   Failures: {len(result.failures)}")
            print(f"   Errors: {len(result.errors)}")
            print("   These issues need to be addressed before deployment.")
        
        return result.wasSuccessful()

def main():
    """Main test runner function"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        runner = NamingTestRunner()
        
        if command == 'critical':
            success = runner.run_critical_tests_only()
        elif command in ['version', 'parsing', 'generation']:
            category_map = {
                'version': 'Version Extraction',
                'parsing': 'Project Parsing', 
                'generation': 'Name Generation'
            }
            success = runner.run_specific_category(category_map[command])
        elif command == 'all':
            success = runner.run_all_tests()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: all, critical, version, parsing, generation")
            return False
    else:
        # Default: run all tests
        runner = NamingTestRunner()
        success = runner.run_all_tests()
    
    return success

if __name__ == '__main__':
    success = main()
    
    if success:
        print("\n🎉 TEST SUITE COMPLETED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n💥 TEST SUITE FAILED!")
        sys.exit(1)