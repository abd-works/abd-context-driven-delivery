// Runs the shared story on {{Aggregate}}Service and {{Aggregate}}RepositorySql against a throwaway database with the
// service's migrations applied. Nothing is stubbed.
import { {{Screen}}Story } from './{snake}.story.shared';
import { throwawayDatabase } from 'test-utils/story-test/throwaway-database';

beforeAll(() => throwawayDatabase.migrate('{service}'));
{{Screen}}Story.runAll({ tier: 'service' });
