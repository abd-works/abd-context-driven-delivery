import { story, scenario } from '../../story-test';
import { ExplorePracticeGraphsServerHelper } from './helpers/explore-practice-graphs.server';
import {
  KEEP_OPERATIONS_SMALL_FOCUSED,
  failingProcessEverythingOperation,
  passingLoadOperation,
} from './helpers/explore-practice-graphs.base';

const helper = new ExplorePracticeGraphsServerHelper();

story('Browse Practice Graphs', () => {
  scenario('KnowledgeGraph lists PracticeGraphs and Nodes', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer browses the KnowledgeGraph', async () => {
      await helper.browse();
    });
    then('the passing Node lists keep-operations-small-focused as passing', () => {
      expect(helper.passingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'passing',
      );
    }).and('the failing Node lists keep-operations-small-focused as violating', () => {
      expect(helper.failingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'violating',
      );
    });
  });
});

story('Open Node Source', () => {
  scenario('file Node opens source and highlights range', ({ given, when, then }) => {
    given('a KnowledgeGraph with a file Node that has a source file and range', async () => {
      await helper.seed();
    });
    when('the Engineer selects the file Node', async () => {
      await helper.selectNode(passingLoadOperation.node_id);
    });
    then('the source file is shown', () => {
      expect(helper.listed?.source_file?.file).toBe(passingLoadOperation.source?.file);
    }).and('the Node range is highlighted', () => {
      expect(helper.listed?.source_file?.start_line).toBe(
        passingLoadOperation.source?.start_line,
      );
      expect(helper.listed?.source_file?.end_line).toBe(
        passingLoadOperation.source?.end_line,
      );
    });
  });
});

story('Follow Relationship', () => {
  scenario('following a Relationship focuses the target Node', ({ given, when, then }) => {
    given('a Node with a Relationship to a target Node', async () => {
      await helper.seed();
    });
    when('the Engineer follows the Relationship', async () => {
      await helper.followRelationship(passingLoadOperation.node_id);
    });
    then('the target Node is selected', () => {
      expect(helper.listed?.selected_node?.node_id).toBe(passingLoadOperation.node_id);
    }).and('the target source file is shown when the target is a file', () => {
      expect(helper.listed?.source_file?.file).toBe('domain/customer/Customer.ts');
    });
  });
});

story('Filter Graph', () => {
  scenario('tree lists only Nodes that match the filters', ({ given, when, then }) => {
    given('a KnowledgeGraph whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer filters the KnowledgeGraph using violations', async () => {
      await helper.filterGraph();
    }).and('using keep-operations-small-focused', async () => {});
    then('the failing Node is listed', () => {
      expect(helper.failingNode()?.node_id).toBe(
        failingProcessEverythingOperation.node_id,
      );
    }).and('the passing Node is not listed', () => {
      expect(helper.passingNode()).toBeUndefined();
    });
  });
});

story('Select Working Folder', () => {
  scenario('selecting a folder scans it into the KnowledgeGraph', ({ given, when, then }) => {
    given('a folder whose source includes a Node that passes keep-operations-small-focused', async () => {
      await helper.seed();
    }).and(
      'whose source includes a Node that fails keep-operations-small-focused',
      async () => {},
    );
    when('the Engineer selects that folder', async () => {
      await helper.selectFolder();
    });
    then('the passing Node lists keep-operations-small-focused as passing', () => {
      expect(helper.passingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'passing',
      );
    }).and('the failing Node lists keep-operations-small-focused as violating', () => {
      expect(helper.failingNode()?.rule_statuses[KEEP_OPERATIONS_SMALL_FOCUSED]).toBe(
        'violating',
      );
    });
  });
});
