import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const source = resolve(root, "site");
const output = resolve(root, "dist");

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
await cp(source, output, { recursive: true });

const htmlPath = resolve(output, "index.html");
const html = await readFile(htmlPath, "utf8");
const requiredMarkers = [
  "<title>Oh My Skills",
  'id="start-design"',
  'id="learn-project"',
  'aria-label="Start Design learning flow"',
  '/skill:start-design SD-01',
  'aria-label="Learn Project source-learning flow"',
  'aria-label="Focused code repeated with the question"',
  '<strong>Focus keyword</strong>',
  '/skill:learn-project ../my-repository',
  'PROJECT_LEARNING/redis--3a71c9e2/',
  '<strong>PROJECT.json</strong>',
  'id="publish-skill"',
  'aria-label="Publish Skill release workflow"',
  '/skill:publish-skill',
];
for (const marker of requiredMarkers) {
  if (!html.includes(marker)) throw new Error(`Site validation failed: missing ${marker}`);
}

const skillFiles = [
  ["start-design", "skills/start-design/SKILL.md"],
  ["learn-project", "skills/learn-project/SKILL.md"],
];
for (const [name, relativePath] of skillFiles) {
  const contents = await readFile(resolve(root, relativePath), "utf8");
  if (!contents.includes(`name: ${name}`)) {
    throw new Error(`Skill validation failed for ${relativePath}`);
  }
}

await writeFile(resolve(output, ".nojekyll"), "", "utf8");
console.log(`Built and validated static site in ${output}`);
