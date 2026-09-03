import { describe, it, beforeEach, afterEach } from 'vitest';
import { {{SubEpicName}}ServerHelper } from './helpers/{{subEpicSlug}}.server';

// Epic: {{EpicName}} | Sub-Epic: {{SubEpicName}}

describe('{{SubEpicName}}', () => {
  const helper = new {{SubEpicName}}ServerHelper();

  beforeEach(async () => { await helper.cleanup(); });
  afterEach(async () => { await helper.cleanup(); });

  it('happy path — fill from spec-by-example scenario', async () => {
    // Given
    // When
    // Then
  });

  it('failure path — fill from spec-by-example scenario', async () => {
    // Given
    // When
    // Then
  });
});
