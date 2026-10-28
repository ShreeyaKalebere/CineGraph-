import fs from 'node:fs';
import path from 'node:path';
import { closeDriver, verifyConnection, writeQuery } from '../config/neo4j.js';

const POSTERS_DIR = path.resolve('frontend/public/posters');

async function main() {
  await verifyConnection();
  console.log('Updating Neo4j movie nodes with downloaded poster paths...');

  if (!fs.existsSync(POSTERS_DIR)) {
    console.error('Posters directory not found:', POSTERS_DIR);
    return;
  }

  const files = fs.readdirSync(POSTERS_DIR).filter((f) => f.endsWith('.jpg'));
  let updated = 0;

  for (const file of files) {
    const movieId = file.replace(/\.jpg$/, '');
    const posterPath = `/posters/${file}`;
    await writeQuery(
      `MATCH (m:Movie {movieId: $movieId}) SET m.posterPath = $posterPath`,
      { movieId, posterPath },
    );
    updated += 1;
  }

  console.log(`✓ Updated ${updated} movie nodes in Neo4j with local poster paths.`);
}

try {
  await main();
} catch (err) {
  console.error('Error updating Neo4j:', err);
} finally {
  await closeDriver();
}
