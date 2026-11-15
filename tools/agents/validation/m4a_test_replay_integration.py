import unittest
import sys
import json
import hashlib
import copy
import tempfile
import importlib.util
import ast
import subprocess
from pathlib import Path

class M4AReplayIntegrationTest(unittest.TestCase):
    """
    Integration tests for M4A offline-replay mode with synthetic fixtures.
    Validates CLI behavior for valid and invalid inputs, output validation,
    and static safety checks.
    """
    
    @classmethod
    def setUpClass(cls):
        """Run CLI twice and validate deterministic output, cache data."""
        cls.ROOT = Path(__file__).resolve().parents[3]
        cls.CLI_PATH = cls.ROOT / 'tools' / 'offline-target-approach.py'
        cls.CONTRACT_PATH = cls.ROOT / 'docs' / 'm4a-offline-target-contract.json'
        cls.CORPUS_PATH = cls.ROOT / 'docs' / 'm4a-offline-target-fixtures.json'
        
        # Load contract and fixtures data
        with open(cls.CONTRACT_PATH, 'rb') as f:
            cls.contract_data = f.read()
        with open(cls.CORPUS_PATH, 'rb') as f:
            cls.corpus_data = f.read()
            
        cls.contract_sha256 = hashlib.sha256(cls.contract_data).hexdigest()
        cls.fixtures_sha256 = hashlib.sha256(cls.corpus_data).hexdigest()
        
        # First CLI run
        cls.first_output = cls._run_cli([sys.executable, '-B', str(cls.CLI_PATH)]).encode()
        
        # Second CLI run for determinism check
        cls.second_output = cls._run_cli([sys.executable, '-B', str(cls.CLI_PATH)]).encode()
        
        # Verify deterministic output
        assert cls.first_output == cls.second_output, "CLI output not deterministic"
    
    @classmethod
    def _run_cli(cls, command):
        """Run CLI with subprocess and return stdout."""
        result = subprocess.run(
            command,
            cwd=cls.ROOT,
            capture_output=True,
            text=True,
            timeout=15
        )
        assert result.returncode == 0, f"CLI failed with code {result.returncode}: {result.stderr}"
        return result.stdout
    
    def test_01_valid_output_within_artifacts(self):
        """Test --output valid using TemporaryDirectory inside artifacts."""
        with tempfile.TemporaryDirectory(dir=self.ROOT / 'artifacts') as tmpdir:
            output_path = Path(tmpdir) / 'valid.json'
            result = subprocess.run(
                [sys.executable, '-B', str(self.CLI_PATH), '--output', str(output_path)],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0, f"CLI failed with: {result.stderr}")
            self.assertTrue(output_path.exists(), f"Output file was not created: {output_path}")
            
            with open(output_path, 'rb') as f:
                output_data = f.read()
            self.assertEqual(
                output_data, self.first_output,
                "Output file content doesn't match CLI stdout"
            )
    
    def test_02_second_run_same_path_exit2(self):
        """Second run same path should exit 2."""
        with tempfile.TemporaryDirectory(dir=self.ROOT / 'artifacts') as tmpdir:
            output_path = Path(tmpdir) / 'valid.json'
            result = subprocess.run(
                [sys.executable, '-B', str(self.CLI_PATH), '--output', str(output_path)],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 0, f"First run failed: {result.stderr}")
            self.assertTrue(output_path.exists(), f"First output file was not created: {output_path}")
            
            # Second run with same path - should exit with code 2
            result2 = subprocess.run(
                [sys.executable, '-B', str(self.CLI_PATH), '--output', str(output_path)],
                capture_output=True,
                text=True
            )
            self.assertEqual(result2.returncode, 2, f"Second run should exit 2, got {result2.returncode}")
            
            with open(output_path, 'rb') as f:
                content = f.read()
            self.assertEqual(content, self.first_output, "Output file was modified")
    
    def test_03_forbidden_output_outside_artifacts(self):
        """Forbidden output outside artifacts should be rejected."""
        with tempfile.TemporaryDirectory(dir=self.ROOT / 'artifacts') as tmpdir:
            forbidden_path = self.ROOT / 'docs' / ('forbidden-' + Path(tmpdir).name + '.json')
            self.assertFalse(forbidden_path.exists(), f"File should not exist: {forbidden_path}")
            
            result = subprocess.run(
                [sys.executable, '-B', str(self.CLI_PATH), '--output', str(forbidden_path)],
                capture_output=True,
                text=True
            )
            self.assertEqual(result.returncode, 2, f"Should reject output outside artifacts: {result.stderr}")
            self.assertFalse(
                forbidden_path.exists(), f"File should not be created: {forbidden_path}"
            )
    
    def test_04_cli_returns_code_2_on_invalid_output_path(self):
        """Test --output with invalid path (like directory) returns code 2."""
        invalid_path = self.ROOT / 'docs' / 'nonexistent' / 'subdir' / 'file.json'
        result = subprocess.run(
            [sys.executable, '-B', str(self.CLI_PATH), '--output', str(invalid_path)],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 2, f"Should reject invalid path: {result.stderr}")
        self.assertFalse(invalid_path.exists(), f"File should not be created: {invalid_path}")
    
    def test_05_json_structure_keys_present(self):
        """Verify CLI JSON has required keys."""
        output = json.loads(self.first_output.decode())
        required_keys = ['mode', 'inputSource', 'caseCount', 'totalSamples', 'passedCases', 'failedCases', 'observedInGame', 'nativePathfindingVerified', 'gameInputSent', 'commandsIssued', 'ok', 'cases']
        for key in required_keys:
            self.assertIn(key, output, f"Missing required key: {key}")
    
    def test_06_json_structure_values(self):
        """Verify CLI JSON has expected values."""
        output = json.loads(self.first_output.decode())
        self.assertEqual(output['mode'], 'offline-replay-only')
        self.assertEqual(output['inputSource'], 'synthetic-fixture')
        self.assertEqual(output['caseCount'], 13)
        self.assertEqual(output['totalSamples'], 24)
        self.assertEqual(output['passedCases'], 13)
        self.assertEqual(output['failedCases'], 0)
        self.assertEqual(output['observedInGame'], False)
        self.assertEqual(output['nativePathfindingVerified'], False)
        self.assertEqual(output['gameInputSent'], False)
        self.assertEqual(output['commandsIssued'], 0)
        self.assertEqual(output['ok'], True)
    
    def test_07_contract_and_fixtures_hash(self):
        """Verify contract and fixtures hashes match cached values."""
        output = json.loads(self.first_output.decode())
        self.assertEqual(output.get('contractSha256'), self.contract_sha256)
        self.assertEqual(output.get('fixturesSha256'), self.fixtures_sha256)
    
    def test_08_all_cases_present(self):
        """Verify all 13 cases are present in output."""
        output = json.loads(self.first_output.decode())
        self.assertEqual(len(output['cases']), 13)
    
    def test_09_cli_imports_check(self):
        """Static analysis: CLI should not import forbidden modules."""
        with open(self.CLI_PATH, 'r') as f:
            source = f.read()
        
        tree = ast.parse(source)
        forbidden_imports = ['subprocess', 'ctypes', 'socket', 'requests', 'win32api', 'win32gui', 'psutil']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_imports:
                        self.fail(f"CLI imports forbidden module: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module in forbidden_imports:
                    self.fail(f"CLI imports forbidden module: {node.module}")
    
    def test_missing_replay_contract_fields_fail_closed_without_keyerror(self):
        spec = importlib.util.spec_from_file_location('offline_target_approach', self.CLI_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original_contract = json.loads(self.contract_data)
        original_corpus = json.loads(self.corpus_data)
        for field in ('terminalStates', 'stateVocabulary', 'exactBuildSha256', 'policy'):
            with self.subTest(missingContractField=field):
                contract = copy.deepcopy(original_contract)
                del contract[field]
                result = module.replay(contract, original_corpus)
                self.assertEqual(result['error'], 'locked-fixture-audit-failed')
                self.assertFalse(result['ok'])
                self.assertFalse(result['gameInputSent'])
                self.assertEqual(result['commandsIssued'], 0)
        corpus = copy.deepcopy(original_corpus)
        del corpus['fixtureSetId']
        result = module.replay(original_contract, corpus)
        self.assertEqual(result['error'], 'locked-fixture-audit-failed')
        self.assertFalse(result['gameInputSent'])

    def test_10_malformed_coordinate_in_corpus(self):
        """Test with malformed coordinate (string instead of numeric coordinate) returns ok false."""
        original = json.loads(self.corpus_data)
        bad = copy.deepcopy(original)
        bad['cases'][0]['samples'][0]['player']['x'] = 'bad-number'
        
        contract = json.loads(self.contract_data)
        
        # Load CLI module dynamically
        spec = importlib.util.spec_from_file_location('offline_target_approach', self.CLI_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call replay with modified data
        r = module.replay(contract, bad)
        self.assertFalse(r['ok'])
        self.assertEqual(r['commandsIssued'], 0)
        self.assertFalse(r['gameInputSent'])
    
    def test_exact_golden_states(self):
        """Test exact golden states per case ID."""
        output = json.loads(self.first_output.decode())
        
        golden_states = {
            'already-arrived': ['arrived'],
            'approach-then-arrive': ['approach-intent', 'approach-intent', 'arrived'],
            'no-progress': ['approach-intent', 'approach-intent', 'no-progress'],
            'moving-away': ['approach-intent', 'moving-away'],
            'stale-telemetry': ['approach-intent', 'telemetry-stale'],
            'target-changed': ['approach-intent', 'target-changed'],
            'operator-cancel': ['approach-intent', 'cancelled'],
            'unsafe-height': ['height-unsafe'],
            'target-unavailable': ['target-unavailable'],
            'invalid-coordinate': ['invalid-sample'],
            'nonmonotonic-time': ['approach-intent', 'invalid-sample'],
            'scene-changed': ['approach-intent', 'scene-changed'],
            'terminal-latched': ['arrived', 'arrived']
        }
        
        for case in output['cases']:
            case_id = case['caseId']
            expected_states = golden_states[case_id]
            self.assertEqual(case['states'], expected_states)
            self.assertTrue(case['matchesExpected'])
            self.assertEqual(case['terminalState'], expected_states[-1])
    
    def test_terminal_latched(self):
        """Test case terminal-latched has trace second item ignoredAfterTerminal=True."""
        output = json.loads(self.first_output.decode())
        
        found = False
        for case in output['cases']:
            if case['caseId'] == 'terminal-latched':
                found = True
                self.assertEqual(len(case['trace']), 2)
                self.assertEqual(case['trace'][0]['state'], 'arrived')
                self.assertEqual(case['trace'][1]['state'], 'arrived')
                self.assertTrue(case['trace'][1].get('ignoredAfterTerminal', False))
        self.assertTrue(found, "terminal-latched case not found")
    
    def test_live_source_fail_closed(self):
        """Test with source.kind='live-game' returns failure."""
        original = json.loads(self.corpus_data)
        bad = copy.deepcopy(original)
        bad['source']['kind'] = 'live-game'
        
        contract = json.loads(self.contract_data)
        
        # Load CLI module dynamically
        spec = importlib.util.spec_from_file_location('offline_target_approach', self.CLI_PATH)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Call replay with modified data
        r = module.replay(contract, bad)
        self.assertFalse(r['ok'])
        self.assertEqual(r['commandsIssued'], 0)
        self.assertFalse(r['gameInputSent'])
    
    def test_stdout_determinism(self):
        """Test stdout determinism and 13 cases parsed."""
        self.assertEqual(self.first_output, self.second_output)
        output = json.loads(self.first_output.decode())
        self.assertEqual(output['caseCount'], 13)
        self.assertEqual(output['passedCases'], 13)
        self.assertEqual(output['failedCases'], 0)
        self.assertEqual(output['ok'], True)

if __name__ == '__main__':
    unittest.main()