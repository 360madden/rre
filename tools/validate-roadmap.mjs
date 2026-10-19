#!/usr/bin/env node
// Manager-owned, read-only consistency check for ROADMAP.md + docs/roadmap-tasks.json.
// Run: node tools/validate-roadmap.mjs from any directory.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const boardPath = path.join(root, 'docs', 'roadmap-tasks.json');
const roadmapPath = path.join(root, 'ROADMAP.md');
const board = JSON.parse(fs.readFileSync(boardPath, 'utf8'));
const roadmap = fs.readFileSync(roadmapPath, 'utf8');
const failures = [];
const check = (ok, detail) => { if (!ok) failures.push(detail); };
const allowed = new Set(board.statusVocabulary || []);
const milestones = new Map();
const tasks = new Map();

check(board.schemaVersion === 1, 'Unexpected task-board schema version.');
check(board.repo === 'C:/work/rre', 'Unexpected primary repo.');
check(/^[0-9a-f]{64}$/.test(board.build?.sha256 || ''), 'Missing exact-build SHA256.');
check(roadmap.includes('M0') && roadmap.includes('M7'), 'Roadmap milestone text missing.');
check(roadmap.includes('Reuse first') && roadmap.includes('T0') && roadmap.includes('T2'), 'Reuse/live gate missing.');
check(board.coordination?.oneWriterPerFile === true, 'Exclusive-file ownership not enforced.');
check(board.coordination?.noLiveInputWithoutSeparateExplicitApproval === true, 'Live-input gate not enforced.');
check(board.coordination?.availableIndependentAiWorkerCount === null ||
      (Number.isInteger(board.coordination.availableIndependentAiWorkerCount) &&
       board.coordination.availableIndependentAiWorkerCount >= 0), 'Invalid actual AI-agent capacity.');

for (const m of board.milestones || []) {
  check(!milestones.has(m.id), 'Duplicate milestone: ' + m.id);
  check(allowed.has(m.status), 'Unrecognized milestone state: ' + m.id);
  milestones.set(m.id, m);
}
for (const t of board.tasks || []) {
  check(!tasks.has(t.id), 'Duplicate task: ' + t.id);
  check(allowed.has(t.status), 'Unrecognized task state: ' + t.id);
  check(milestones.has(t.milestone), 'Missing milestone for task: ' + t.id);
  check(t.lane === 'manager' || Boolean(board.coordination.workerLanes[t.lane]),
        'Unknown lane: ' + t.id);
  check(Array.isArray(t.acceptance) && t.acceptance.length > 0,
        'Missing task acceptance criteria: ' + t.id);
  check(typeof t.deliverable === 'string' && t.deliverable.length > 0,
        'Missing task deliverable: ' + t.id);
  if (t.status === 'integrated') {
    check(/^[0-9a-f]{40}$/.test(t.integratedCommit || ''),
          'Integrated task missing commit: ' + t.id);
  }
  if (t.status === 'running') {
    check(Boolean(t.jobId) && Boolean(t.assignedAgentId),
          'Running task missing real agent/job ID: ' + t.id);
  } else {
    check(t.jobId === null, 'Non-running task retaining job ID: ' + t.id);
  }
  if (t.status === 'blocked') {
    check((t.blockers || []).length > 0, 'Blocked task missing reason: ' + t.id);
  }
  tasks.set(t.id, t);
}
for (const m of milestones.values()) for (const dep of m.dependsOn || [])
  check(milestones.has(dep) && dep !== m.id, 'Bad milestone dependency: ' + m.id + ' -> ' + dep);
for (const t of tasks.values()) for (const dep of t.dependsOn || [])
  check(tasks.has(dep) && dep !== t.id, 'Bad task dependency: ' + t.id + ' -> ' + dep);

// Detect cycles by depth-first search; do not let a coordinator schedule impossible work.
function validateDAG(nodes, label) {
  const visited = new Set(), visiting = new Set();
  function walk(id) {
    if (visiting.has(id)) { failures.push(label + ' dependency cycle at ' + id); return; }
    if (visited.has(id)) return;
    visiting.add(id);
    for (const dep of nodes.get(id)?.dependsOn || []) if (nodes.has(dep)) walk(dep);
    visiting.delete(id);
    visited.add(id);
  }
  for (const id of nodes.keys()) walk(id);
}
validateDAG(milestones, 'Milestone');
validateDAG(tasks, 'Task');

const laneWrites = new Map();
for (const [lane, config] of Object.entries(board.coordination.workerLanes || {})) {
  check(config.branch === 'research/nav-' + lane, 'Unexpected branch for lane: ' + lane);
  check(config.worktree.toLowerCase().endsWith('rre-worker-' + lane),
        'Unexpected worktree for lane: ' + lane);
  for (const owned of config.owned || []) {
    const prev = laneWrites.get(owned);
    check(!prev || prev === lane, 'Cross-lane duplicate writable pattern: ' + owned);
    laneWrites.set(owned, lane);
  }
}
const running = (board.tasks || []).filter(t => t.status === 'running');
for (const [lane] of Object.entries(board.coordination.workerLanes || {}))
  check(running.filter(t => t.lane === lane).length <= 1,
        'Concurrent tasks share one worker lane: ' + lane);
check((tasks.get('M5-T1')?.dependsOn || []).includes('M5-T0'), 'T1 must depend on T0.');
check((tasks.get('M5-T2')?.dependsOn || []).includes('M5-T1'), 'T2 must depend on T1.');

const statusCounts = {};
for (const t of tasks.values()) statusCounts[t.status] = (statusCounts[t.status] || 0) + 1;
const result = {
  ok: failures.length === 0,
  roadmap: 'ROADMAP.md',
  board: 'docs/roadmap-tasks.json',
  milestones: milestones.size,
  tasks: tasks.size,
  activeRecordedAgentJobs: running.length,
  statusCounts,
  failures
};
process.stdout.write(JSON.stringify(result, null, 2) + '\n');
if (failures.length) process.exitCode = 1;
