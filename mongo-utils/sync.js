import 'dotenv/config';
import { MongoClient } from 'mongodb';
import inquirer from 'inquirer';

const EXCLUDED_DBS = new Set(['admin', 'config', 'local']);
const BATCH_SIZE = 500;

async function syncCollection(sourceCol, targetCol) {
  let upserted = 0, modified = 0, unchanged = 0;
  let batch = [];

  const flush = async () => {
    if (batch.length === 0) return;
    const result = await targetCol.bulkWrite(batch, { ordered: false });
    upserted += result.upsertedCount;
    modified += result.modifiedCount;
    unchanged += result.matchedCount - result.modifiedCount;
    batch = [];
  };

  for await (const doc of sourceCol.find()) {
    batch.push({
      replaceOne: { filter: { _id: doc._id }, replacement: doc, upsert: true },
    });
    if (batch.length >= BATCH_SIZE) await flush();
  }
  await flush();

  // Find documents in target that don't exist in source
  const sourceIds = await sourceCol.distinct('_id');
  const orphans = await targetCol.countDocuments({ _id: { $nin: sourceIds } });

  return { upserted, modified, unchanged, orphans };
}

async function main() {
  const { SOURCE_URI, TARGET_URI } = process.env;

  if (!SOURCE_URI || !TARGET_URI) {
    console.error('ERROR: SOURCE_URI and TARGET_URI must be set in .env');
    process.exit(1);
  }

  const source = new MongoClient(SOURCE_URI);
  const target = new MongoClient(TARGET_URI);

  try {
    process.stdout.write('Connecting to source and target... ');
    await Promise.all([source.connect(), target.connect()]);
    console.log('OK\n');

    const { databases } = await source.db('admin').admin().listDatabases();
    const available = databases
      .map((d) => d.name)
      .filter((n) => !EXCLUDED_DBS.has(n))
      .sort();

    if (available.length === 0) {
      console.log('No user databases found on source.');
      return;
    }

    const { selected } = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'selected',
        message: 'Select databases to sync (space to toggle, enter to confirm):',
        choices: available,
        validate: (v) => v.length > 0 || 'Select at least one database.',
      },
    ]);

    console.log();
    const report = {};

    for (const dbName of selected) {
      console.log(`── ${dbName}`);
      const sourceDb = source.db(dbName);
      const targetDb = target.db(dbName);

      const collections = await sourceDb.listCollections().toArray();
      report[dbName] = {};

      if (collections.length === 0) {
        console.log('   (no collections)\n');
        continue;
      }

      for (const { name } of collections) {
        process.stdout.write(`   ${name.padEnd(32)}`);
        const stats = await syncCollection(
          sourceDb.collection(name),
          targetDb.collection(name)
        );
        report[dbName][name] = stats;

        const parts = [
          `+${stats.upserted} new`,
          `~${stats.modified} updated`,
          `=${stats.unchanged} unchanged`,
          stats.orphans > 0 ? `! ${stats.orphans} orphaned` : null,
        ].filter(Boolean);

        console.log(parts.join('   '));
      }

      console.log();
    }

    // Summary
    console.log('══ SYNC SUMMARY ══════════════════════════════════════════════');

    let totalNew = 0, totalUpdated = 0, totalUnchanged = 0, totalOrphans = 0;

    for (const [db, cols] of Object.entries(report)) {
      const colEntries = Object.entries(cols);
      if (colEntries.length === 0) continue;
      console.log(`\n  ${db}`);
      for (const [col, s] of colEntries) {
        const orphanNote = s.orphans > 0 ? `,   ! ${s.orphans} orphaned in target` : '';
        console.log(`    ${col}: +${s.upserted} new, ~${s.modified} updated, =${s.unchanged} unchanged${orphanNote}`);
        totalNew += s.upserted;
        totalUpdated += s.modified;
        totalUnchanged += s.unchanged;
        totalOrphans += s.orphans;
      }
    }

    console.log('\n──────────────────────────────────────────────────────────────');
    console.log(
      `  TOTAL  +${totalNew} new   ~${totalUpdated} updated   =${totalUnchanged} unchanged   ! ${totalOrphans} orphaned`
    );

    if (totalOrphans > 0) {
      console.log(
        '\n  NOTE: Orphaned documents exist in the target but not the source.'
      );
      console.log(
        '  This sync is additive — they were left in place. Review manually if needed.'
      );
    }
  } finally {
    await Promise.all([source.close(), target.close()]);
  }
}

main().catch((err) => {
  console.error('\nFatal error:', err.message);
  process.exit(1);
});
