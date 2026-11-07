"""Failure-path checks for the disposable host fixture cleanup, no OS process calls."""
import importlib.util
from pathlib import Path
import subprocess
import unittest

spec = importlib.util.spec_from_file_location('native_probe', Path(__file__).with_name('probe-native-publication.py'))
probe = importlib.util.module_from_spec(spec); spec.loader.exec_module(probe)


class Child:
    def __init__(self, broken=False, exits_on='graceful', already=False):
        self.returncode = 0 if already else None
        self.broken, self.exits_on, self.actions = broken, exits_on, []
        self.stdin = self
    def poll(self): return self.returncode
    def write(self, text):
        self.actions.append('stdin')
        if self.broken: raise BrokenPipeError('synthetic')
    def flush(self): pass
    def terminate(self): self.actions.append('terminate')
    def kill(self): self.actions.append('kill')
    def wait(self, timeout):
        action = next((a for a in reversed(self.actions) if a in ['terminate', 'kill']), 'graceful')
        if action != self.exits_on: raise subprocess.TimeoutExpired('synthetic', timeout)
        self.returncode = 0 if action == 'graceful' else 1


class CleanupTests(unittest.TestCase):
    def test_already_exited_is_untouched(self):
        child=Child(already=True); result=probe.cleanup_fixture(child)
        self.assertTrue(result['fixtureExited']); self.assertEqual(child.actions, [])
    def test_graceful_exit(self):
        child=Child(); result=probe.cleanup_fixture(child)
        self.assertTrue(result['fixtureExited']); self.assertEqual(result['cleanupErrors'], [])
    def test_broken_stdin_still_reaches_final_kill(self):
        child=Child(broken=True, exits_on='kill'); result=probe.cleanup_fixture(child)
        self.assertTrue(result['fixtureExited']); self.assertEqual(child.actions, ['stdin','terminate','kill'])
        self.assertEqual(result['cleanupErrors'], ['graceful-stdin-BrokenPipeError','graceful-TimeoutExpired','terminate-TimeoutExpired'])
    def test_all_timeouts_return_explicit_incomplete_receipt(self):
        child=Child(exits_on='never'); result=probe.cleanup_fixture(child)
        self.assertFalse(result['fixtureExited']); self.assertIsNone(result['fixtureExitCode'])
        self.assertIn('kill-TimeoutExpired',result['cleanupErrors'])


if __name__ == '__main__': unittest.main()
