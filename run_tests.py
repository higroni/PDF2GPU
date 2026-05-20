#!/usr/bin/env python3
"""
Automatski test runner za PDF2GPU projekat.
Pokreće testove za određenu fazu i generiše izveštaj.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class TestRunner:
    def __init__(self, phase: str):
        self.phase = phase
        self.results = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {}
        }
    
    def run_backend_tests(self, test_path: str) -> Tuple[bool, Dict]:
        """Pokreće Python testove sa pytest"""
        print(f"\n🧪 Pokretanje backend testova: {test_path}")
        
        cmd = [
            "pytest",
            test_path,
            "-v",                          # Verbose
            "--cov=backend",               # Coverage
            "--cov-report=term-missing",   # Prikaži missing lines
            "--cov-report=json",           # JSON izveštaj
            "--tb=short",                  # Kraći traceback
            "--color=yes"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse coverage
        coverage_data = {}
        if Path("coverage.json").exists():
            with open("coverage.json") as f:
                coverage_data = json.load(f)
        
        return result.returncode == 0, {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "coverage": coverage_data.get("totals", {}).get("percent_covered", 0)
        }
    
    def run_frontend_tests(self, test_path: str) -> Tuple[bool, Dict]:
        """Pokreće TypeScript testove sa Jest"""
        print(f"\n🧪 Pokretanje frontend testova: {test_path}")
        
        cmd = [
            "npm",
            "test",
            "--",
            test_path,
            "--coverage",
            "--watchAll=false",
            "--json",
            "--outputFile=jest-results.json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="frontend")
        
        # Parse results
        jest_data = {}
        if Path("frontend/jest-results.json").exists():
            with open("frontend/jest-results.json") as f:
                jest_data = json.load(f)
        
        return result.returncode == 0, {
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr,
            "coverage": jest_data.get("coverageMap", {})
        }
    
    def run_phase_tests(self) -> bool:
        """Pokreće sve testove za određenu fazu"""
        phase_config = {
            "phase1": {
                "backend": ["tests/phase1_backend_core/"],
                "frontend": []
            },
            "phase2": {
                "backend": [],
                "frontend": ["tests/phase2_frontend_core/"]
            },
            "phase3": {
                "backend": ["tests/phase3_test_examples/"],
                "frontend": []
            },
            "phase4": {
                "backend": ["tests/phase4_version_comparison/"],
                "frontend": ["tests/phase4_version_comparison/"]
            },
            "phase5": {
                "backend": ["tests/phase5_feedback/"],
                "frontend": []
            },
            "phase6": {
                "backend": ["tests/phase6_session_logging/"],
                "frontend": []
            },
            "phase7": {
                "backend": ["tests/phase7_integration/"],
                "frontend": []
            },
            "phase8": {
                "backend": ["tests/phase8_deployment/"],
                "frontend": []
            }
        }
        
        config = phase_config.get(self.phase, {})
        all_passed = True
        
        # Backend testovi
        for test_path in config.get("backend", []):
            passed, results = self.run_backend_tests(test_path)
            self.results["tests"][test_path] = results
            all_passed = all_passed and passed
        
        # Frontend testovi
        for test_path in config.get("frontend", []):
            passed, results = self.run_frontend_tests(test_path)
            self.results["tests"][test_path] = results
            all_passed = all_passed and passed
        
        return all_passed
    
    def generate_report(self):
        """Generiše test izveštaj"""
        total_tests = len(self.results["tests"])
        passed_tests = sum(1 for t in self.results["tests"].values() if t["passed"])
        
        self.results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        # Sačuvaj JSON izveštaj
        report_path = f"test_reports/{self.phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        Path("test_reports").mkdir(exist_ok=True)
        
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        # Prikaži summary
        print("\n" + "="*60)
        print(f"📊 TEST IZVEŠTAJ - {self.phase.upper()}")
        print("="*60)
        print(f"Ukupno testova: {total_tests}")
        print(f"✅ Prošlo: {passed_tests}")
        print(f"❌ Palo: {total_tests - passed_tests}")
        print(f"📈 Pass Rate: {self.results['summary']['pass_rate']:.1f}%")
        print(f"\n📄 Detaljan izveštaj: {report_path}")
        print("="*60)
        
        return self.results["summary"]["pass_rate"] >= 80  # Minimum 80% pass rate

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_tests.py <phase>")
        print("Phases: phase1, phase2, phase3, phase4, phase5, phase6, phase7, phase8")
        sys.exit(1)
    
    phase = sys.argv[1]
    runner = TestRunner(phase)
    
    print(f"\n🚀 Pokretanje testova za {phase.upper()}")
    
    tests_passed = runner.run_phase_tests()
    report_ok = runner.generate_report()
    
    if tests_passed and report_ok:
        print("\n✅ SVI TESTOVI SU PROŠLI! Možeš nastaviti na sledeću fazu.")
        sys.exit(0)
    else:
        print("\n❌ TESTOVI NISU PROŠLI! Ispravi greške pre nego što nastaviš.")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Made with Bob
