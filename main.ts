import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';

// Copy POST.json from repo root to /output for make.fun submission
const content = readFileSync('./POST.json', 'utf8');
mkdirSync('/output', { recursive: true });
writeFileSync('/output/POST.json', content);
