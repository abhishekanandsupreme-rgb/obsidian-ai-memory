#!/usr/bin/env node
// browseros-bridge.js — BrowserOS Neo bridge that syncs browser automation logs to Obsidian.
//
// Usage:
//   node browseros-bridge.js <browseros_log_path> <agent_id>
//   node browseros-bridge.js "C:/Users/asus/AppData/Local/BrowserOS/User Data/.browseros/browseros-server.log" browseros
//
// All paths are absolute. Does not modify any BrowserOS or agent configs.
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SYNC_SCRIPT = 'C:/Users/asus/Documents/Obsidian Vault/scripts/sync-to-obsidian.py';
const PYTHON = process.env.PYTHON || 'python';
const DEFAULT_AGENT_ID = 'browseros';

function readLog(logPath) {
  if (!fs.existsSync(logPath)) {
    console.error(`[WARN] BrowserOS log not found: ${logPath}`);
    return null;
  }
  return fs.readFileSync(logPath, 'utf-8');
}

function extractSummary(logText) {
  const lines = logText.split(/\r?\n/).filter(Boolean);
  const lastLines = lines.slice(-20).join('\n');
  return lastLines || 'BrowserOS automation log summary';
}

function syncToObsidian(agentId, sessionData) {
  const payload = JSON.stringify({ sessionData });
  const cmd = `${PYTHON} "${SYNC_SCRIPT}" --agent-id "${agentId}" --session-data ${JSON.stringify(payload)} --vault-path "C:/Users/asus/Documents/Obsidian Vault"`;

  try {
    const out = execSync(cmd, { encoding: 'utf-8' });
    console.log('[INFO] BrowserOS log synced to Obsidian.');
    console.log(out.trim());
    return true;
  } catch (e) {
    console.error('[WARN] Obsidian sync failed; continuing.', e.message);
    return false;
  }
}

function main() {
  const args = process.argv.slice(2);
  const logPath = args[0] || 'C:/Users/asus/AppData/Local/BrowserOS/User Data/.browseros/browseros-server.log';
  const agentId = args[1] || DEFAULT_AGENT_ID;

  const logText = readLog(logPath);
  if (!logText) {
    process.exit(0);
  }

  const sessionData = {
    session_id: `browseros-${Date.now()}`,
    started_at: new Date(Date.now() - 60000).toISOString(),
    ended_at: new Date().toISOString(),
    status: 'completed',
    summary: 'BrowserOS automation log sync',
    key_events: extractSummary(logText),
    actions_taken: 'Synced BrowserOS automation logs to Obsidian',
    decisions_made: 'None',
    next_steps: 'Review Obsidian agent memory',
  };

  syncToObsidian(agentId, sessionData);
}

if (require.main === module) {
  main();
}
