import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Copy POST.json from repo root to /output for make.fun submission.
// Resolve paths from the script's own directory (the grader runs
// `node /bot/main.ts` from a different CWD, so './POST.json' fails).
const botDir = process.env.MAKEFUN_BOT_DIR || dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
const content = readFileSync(join(botDir, 'POST.json'), 'utf8');
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'POST.json'), content);
