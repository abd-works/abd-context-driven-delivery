import { expect } from '@playwright/test';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { story, scenario } from '../story-test';
import { PML_DOMAIN, bindPage, explorer, openPmlDomain, waitForTree, waitForWork } from './helpers/pml-domain';

bindPage();

story('Create Database', () => {
  scenario('creating a database writes master and the working copy', ({ given, when, then }) => {
    given('pml-domain is the working folder', async () => {
      await openPmlDomain();
    });
    when('the Engineer creates the database', async () => {
      await explorer().getByTestId('create-database').click();
      await waitForWork('Create database');
    });
    then('master is written', () => {
      expect(existsSync(join(PML_DOMAIN, '.codeql', 'javascript-master'))).toBe(true);
    }).and('master is copied to the working copy', () => {
      expect(existsSync(join(PML_DOMAIN, '.codeql', 'javascript-working-copy'))).toBe(true);
    }).and('the PracticeGraph lists domain', async () => {
      await waitForTree();
    });
  });
});
