// test/{{domain}}/{{domain}}.test.ts
import { describe } from 'vitest';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { {{Domain}} } from '../../src/{{domain}}/{{domain}}.js';
import { {{Domain}}Server } from '../../src/{{domain}}/{{domain}}_server.js';
import { {{Domain}}Test } from './{{domain}}_test.js';
import type { I{{Domain}} } from '../../src/{{domain}}/{{domain}}.js';

// Domain tier — pure class, no persistence
describe('{{Domain}}', () => {
  class Domain{{Domain}}Test extends {{Domain}}Test {
    protected createEntity(): I{{Domain}} {
      return new {{Domain}}();
    }
  }
  new Domain{{Domain}}Test().registerTests();
});

// Server domain tier — verifies persistence after reload
describe('{{Domain}}Server', () => {
  let tmpDir: string;
  let filePath: string;

  // TODO: add beforeEach to set up temp dir
  // beforeEach(() => {
  //   tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), '{{domain}}-'));
  //   filePath = path.join(tmpDir, '{{domain}}.json');
  // });

  class Server{{Domain}}Test extends {{Domain}}Test {
    protected createEntity(): I{{Domain}} {
      return new {{Domain}}Server(filePath);
    }

    protected override assertState(entity: I{{Domain}}, expected: unknown): void {
      super.assertState(entity, expected);
      // TODO: reload and verify persistence
      // const reloaded = new {{Domain}}Server(filePath);
      // expect(reloaded.total).toBe(expected);
    }
  }
  new Server{{Domain}}Test().registerTests();
});
