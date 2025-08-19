# SpecPlane Measurement Tracking System
# Comprehensive metrics collection and analysis for all experiments

import json
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Import system contracts
from specplane.models import (
    ExperimentType, ExperimentRun, ExperimentMetrics, 
    ComponentType, STANDARD_QUALITY_GATES
)


# =============================================================================
# MEASUREMENT COLLECTION
# =============================================================================

class MetricsCollector:
    """Collects and tracks metrics during experiments"""
    
    def __init__(self, data_dir: str = ".specplane/metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.runs_file = self.data_dir / "experiment_runs.jsonl"
        self.metrics_file = self.data_dir / "aggregated_metrics.json"
        
    def start_experiment(self, experiment_type: ExperimentType, component_name: str) -> ExperimentRun:
        """Start tracking a new experiment run"""
        import uuid
        
        run = ExperimentRun(
            id=str(uuid.uuid4()),
            experiment_type=experiment_type,
            component_name=component_name,
            start_time=datetime.now()
        )
        
        print(f"🔬 Starting {experiment_type.value} experiment for {component_name}")
        print(f"   Run ID: {run.id}")
        
        return run
    
    def end_experiment(self, run: ExperimentRun, success: bool, artifacts: List[str] = None) -> ExperimentRun:
        """Complete experiment tracking"""
        run.end_time = datetime.now()
        run.success = success
        run.artifacts_generated = artifacts or []
        
        # Calculate duration
        if run.start_time and run.end_time:
            duration = (run.end_time - run.start_time).total_seconds() / 60
            print(f"📊 Experiment completed in {duration:.1f} minutes")
        
        # Save run data
        self._save_run(run)
        
        # Update aggregated metrics
        self._update_aggregated_metrics()
        
        return run
    
    def record_time_to_green(self, run: ExperimentRun, test_command: str = "make test") -> Optional[float]:
        """Measure time until tests pass"""
        print(f"⏱️  Measuring time-to-green with: {test_command}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                test_command.split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            elapsed_minutes = (time.time() - start_time) / 60
            
            if result.returncode == 0:
                run.time_to_green = elapsed_minutes
                print(f"✅ Tests passed in {elapsed_minutes:.1f} minutes")
                return elapsed_minutes
            else:
                print(f"❌ Tests failed after {elapsed_minutes:.1f} minutes")
                print(f"   Error: {result.stderr[:200]}...")
                return None
                
        except subprocess.TimeoutExpired:
            print("⏰ Test timeout after 5 minutes")
            return None
        except Exception as e:
            print(f"🚨 Error running tests: {e}")
            return None
    
    def record_quality_gates(self, run: ExperimentRun) -> Dict[str, bool]:
        """Run and record quality gate results"""
        print("🚪 Running quality gates...")
        
        gate_results = {}
        
        for gate in STANDARD_QUALITY_GATES:
            print(f"   Testing {gate.name}...")
            
            try:
                result = subprocess.run(
                    gate.command.split(),
                    capture_output=True,
                    text=True,
                    timeout=gate.timeout_seconds
                )
                
                passed = result.returncode == 0
                gate_results[gate.name] = passed
                
                if passed:
                    print(f"   ✅ {gate.name} passed")
                else:
                    print(f"   ❌ {gate.name} failed")
                    print(f"      {result.stderr[:100]}...")
                    
            except subprocess.TimeoutExpired:
                gate_results[gate.name] = False
                print(f"   ⏰ {gate.name} timeout")
            except Exception as e:
                gate_results[gate.name] = False
                print(f"   🚨 {gate.name} error: {e}")
        
        # Count failures for spec drift tracking
        failed_gates = sum(1 for passed in gate_results.values() if not passed)
        run.spec_drift_count = failed_gates
        
        return gate_results
    
    def record_rework_cycle(self, run: ExperimentRun, reason: str):
        """Record a rework iteration"""
        run.rework_cycles += 1
        run.issues_encountered.append(f"Rework #{run.rework_cycles}: {reason}")
        print(f"🔄 Rework cycle #{run.rework_cycles}: {reason}")
    
    def record_editor_friction(self, run: ExperimentRun, description: str):
        """Record manual intervention required"""
        run.editor_friction_count += 1
        run.issues_encountered.append(f"Manual edit #{run.editor_friction_count}: {description}")
        print(f"✏️  Manual edit required: {description}")
    
    def _save_run(self, run: ExperimentRun):
        """Save experiment run to JSONL file"""
        with open(self.runs_file, 'a') as f:
            # Convert to dict and handle datetime serialization
            run_dict = asdict(run)
            run_dict['start_time'] = run.start_time.isoformat() if run.start_time else None
            run_dict['end_time'] = run.end_time.isoformat() if run.end_time else None
            
            f.write(json.dumps(run_dict) + '\n')
    
    def _update_aggregated_metrics(self):
        """Update aggregated metrics across all experiments"""
        metrics_by_type = {}
        
        # Load all runs
        if not self.runs_file.exists():
            return
            
        with open(self.runs_file) as f:
            runs = [json.loads(line) for line in f]
        
        # Group by experiment type
        for run_data in runs:
            exp_type = run_data['experiment_type']
            if exp_type not in metrics_by_type:
                metrics_by_type[exp_type] = []
            metrics_by_type[exp_type].append(run_data)
        
        # Calculate aggregated metrics
        aggregated = {}
        for exp_type, type_runs in metrics_by_type.items():
            total_runs = len(type_runs)
            successful_runs = [r for r in type_runs if r['success']]
            
            # Calculate averages for successful runs
            times_to_green = [r['time_to_green'] for r in successful_runs if r['time_to_green']]
            rework_cycles = [r['rework_cycles'] for r in type_runs]
            quality_scores = [r['final_quality_score'] for r in successful_runs if r['final_quality_score']]
            
            aggregated[exp_type] = {
                'total_runs': total_runs,
                'success_rate': len(successful_runs) / total_runs if total_runs > 0 else 0,
                'avg_time_to_green': sum(times_to_green) / len(times_to_green) if times_to_green else None,
                'avg_rework_cycles': sum(rework_cycles) / len(rework_cycles) if rework_cycles else 0,
                'avg_quality_score': sum(quality_scores) / len(quality_scores) if quality_scores else None
            }
        
        # Save aggregated metrics
        with open(self.metrics_file, 'w') as f:
            json.dump(aggregated, f, indent=2)


# =============================================================================
# EXPERIMENT CONTEXT MANAGER
# =============================================================================

@contextmanager
def track_experiment(experiment_type: ExperimentType, component_name: str, collector: MetricsCollector = None):
    """Context manager for tracking complete experiments"""
    
    if collector is None:
        collector = MetricsCollector()
    
    # Start experiment
    run = collector.start_experiment(experiment_type, component_name)
    
    try:
        yield run, collector
        
        # If we get here, experiment succeeded
        collector.end_experiment(run, success=True)
        
    except Exception as e:
        # Experiment failed
        run.issues_encountered.append(f"Exception: {str(e)}")
        collector.end_experiment(run, success=False)
        print(f"💥 Experiment failed: {e}")
        raise
    
    finally:
        # Always print summary
        _print_experiment_summary(run)


def _print_experiment_summary(run: ExperimentRun):
    """Print experiment summary"""
    print("\n" + "="*50)
    print(f"📋 EXPERIMENT SUMMARY")
    print("="*50)
    print(f"Type: {run.experiment_type.value}")
    print(f"Component: {run.component_name}")
    print(f"Success: {'✅' if run.success else '❌'}")
    
    if run.time_to_green:
        print(f"Time to Green: {run.time_to_green:.1f} minutes")
    
    print(f"Rework Cycles: {run.rework_cycles}")
    print(f"Editor Friction: {run.editor_friction_count}")
    print(f"Spec Drift Issues: {run.spec_drift_count}")
    
    if run.artifacts_generated:
        print(f"Artifacts Generated: {len(run.artifacts_generated)}")
        for artifact in run.artifacts_generated:
            print(f"  - {artifact}")
    
    if run.issues_encountered:
        print(f"Issues Encountered: {len(run.issues_encountered)}")
        for issue in run.issues_encountered[-3:]:  # Show last 3 issues
            print(f"  - {issue}")
    
    print("="*50)


# =============================================================================
# ANALYSIS AND REPORTING
# =============================================================================

class MetricsAnalyzer:
    """Analyze experiment results and generate reports"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def generate_experiment_comparison(self) -> str:
        """Generate comparison report across experiment types"""
        if not self.collector.metrics_file.exists():
            return "No metrics data available yet."
        
        with open(self.collector.metrics_file) as f:
            metrics = json.load(f)
        
        report = "# SpecPlane Experiment Comparison Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Create comparison table
        report += "## Results Summary\n\n"
        report += "| Experiment | Runs | Success Rate | Avg Time to Green | Avg Rework Cycles | Avg Quality Score |\n"
        report += "|------------|------|--------------|-------------------|-------------------|-------------------|\n"
        
        for exp_type, data in metrics.items():
            time_to_green = f"{data['avg_time_to_green']:.1f}m" if data['avg_time_to_green'] else "N/A"
            quality_score = f"{data['avg_quality_score']:.2f}" if data['avg_quality_score'] else "N/A"
            
            report += f"| {exp_type} | {data['total_runs']} | {data['success_rate']:.1%} | {time_to_green} | {data['avg_rework_cycles']:.1f} | {quality_score} |\n"
        
        # Add insights
        report += "\n## Key Insights\n\n"
        
        # Find best performing experiment
        best_success_rate = max(metrics.values(), key=lambda x: x['success_rate'])
        best_experiment = next(exp for exp, data in metrics.items() if data == best_success_rate)
        report += f"- **Highest Success Rate**: {best_experiment} ({best_success_rate['success_rate']:.1%})\n"
        
        # Find fastest experiment
        fastest_times = {exp: data['avg_time_to_green'] for exp, data in metrics.items() if data['avg_time_to_green']}
        if fastest_times:
            fastest_experiment = min(fastest_times, key=fastest_times.get)
            report += f"- **Fastest to Green**: {fastest_experiment} ({fastest_times[fastest_experiment]:.1f} minutes)\n"
        
        # Find lowest rework
        lowest_rework = min(metrics.values(), key=lambda x: x['avg_rework_cycles'])
        lowest_rework_exp = next(exp for exp, data in metrics.items() if data == lowest_rework)
        report += f"- **Lowest Rework**: {lowest_rework_exp} ({lowest_rework['avg_rework_cycles']:.1f} cycles)\n"
        
        return report
    
    def get_component_trends(self, component_name: str) -> Dict[str, Any]:
        """Analyze trends for specific component across experiments"""
        if not self.collector.runs_file.exists():
            return {}
        
        with open(self.collector.runs_file) as f:
            runs = [json.loads(line) for line in f if json.loads(line)['component_name'] == component_name]
        
        if not runs:
            return {}
        
        return {
            'total_attempts': len(runs),
            'success_rate': sum(1 for r in runs if r['success']) / len(runs),
            'avg_time_to_green': sum(r['time_to_green'] for r in runs if r['time_to_green']) / len([r for r in runs if r['time_to_green']]),
            'total_rework_cycles': sum(r['rework_cycles'] for r in runs),
            'improvement_trend': self._calculate_improvement_trend(runs)
        }
    
    def _calculate_improvement_trend(self, runs: List[Dict]) -> str:
        """Calculate if metrics are improving over time"""
        if len(runs) < 2:
            return "insufficient_data"
        
        # Sort by start time
        sorted_runs = sorted(runs, key=lambda x: x['start_time'])
        
        # Compare first half vs second half
        midpoint = len(sorted_runs) // 2
        first_half = sorted_runs[:midpoint]
        second_half = sorted_runs[midpoint:]
        
        first_half_success = sum(1 for r in first_half if r['success']) / len(first_half)
        second_half_success = sum(1 for r in second_half if r['success']) / len(second_half)
        
        if second_half_success > first_half_success + 0.1:
            return "improving"
        elif second_half_success < first_half_success - 0.1:
            return "declining"
        else:
            return "stable"


# =============================================================================
# USAGE EXAMPLES AND HELPERS
# =============================================================================

def run_component_experiment(experiment_type: ExperimentType, component_name: str, test_command: str = "make test"):
    """Complete experiment runner with full tracking"""
    
    collector = MetricsCollector()
    
    with track_experiment(experiment_type, component_name, collector) as (run, collector):
        print(f"🚀 Ready to implement {component_name} using {experiment_type.value}")
        print("💡 Follow these steps:")
        print("   1. Implement the component")
        print("   2. Run tests when ready")
        print("   3. Record any rework cycles")
        print("   4. Record manual edits")
        
        # Wait for user to indicate they're done implementing
        input("⏸️  Press Enter when implementation is complete...")
        
        # Measure time to green
        time_to_green = collector.record_time_to_green(run, test_command)
        
        # Run quality gates
        gate_results = collector.record_quality_gates(run)
        
        # Check if all gates passed
        all_passed = all(gate_results.values())
        
        if not all_passed:
            print("⚠️  Some quality gates failed. Recording as rework cycle.")
            collector.record_rework_cycle(run, "Quality gates failed")
        
        # Record final quality score (you could make this more sophisticated)
        run.final_quality_score = sum(gate_results.values()) / len(gate_results)
        
        print(f"🎯 Final Quality Score: {run.final_quality_score:.2f}")
        
        return run


def interactive_experiment_runner():
    """Interactive CLI for running experiments"""
    print("🔬 SpecPlane Experiment Runner")
    print("="*40)
    
    # Select experiment type
    print("\nAvailable experiment types:")
    for i, exp_type in enumerate(ExperimentType, 1):
        print(f"{i}. {exp_type.value}")
    
    choice = int(input("\nSelect experiment type (1-5): ")) - 1
    experiment_type = list(ExperimentType)[choice]
    
    # Enter component name
    component_name = input("Enter component name: ")
    
    # Enter test command (optional)
    test_command = input("Test command (default: make test): ").strip() or "make test"
    
    # Run experiment
    run = run_component_experiment(experiment_type, component_name, test_command)
    
    # Generate quick report
    analyzer = MetricsAnalyzer(MetricsCollector())
    print("\n" + analyzer.generate_experiment_comparison())


# =============================================================================
# CLI INTEGRATION
# =============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_experiment_runner()
    else:
        print("Usage:")
        print("  python measurement_tracking.py interactive")
        print("\nOr use programmatically:")
        print("  from measurement_tracking import track_experiment, MetricsCollector")
        print("  with track_experiment(ExperimentType.COMPONENT_KERNEL, 'File_Storage') as (run, collector):")
        print("      # implement component")
        print("      collector.record_time_to_green(run)")