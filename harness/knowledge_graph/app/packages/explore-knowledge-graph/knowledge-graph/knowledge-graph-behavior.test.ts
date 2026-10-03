import {
  KnowledgeGraph,
  KnowledgeGraphCallSource,
  KnowledgeGraphFilter,
  KnowledgeGraphNode,
  KnowledgeGraphSourceFold,
  editorHeight,
  isStoryNode,
  practiceRootLabels,
  restoredBranches,
  databaseBuildRequired,
  databaseGraphFromScratch,
  extractionProgress,
  ruleChoices,
  rulesForFilters,
  domainTree,
  dddClassKind,
  retainedTree,
  retagPractice,
  shownRelationships,
  stepMembers,
  stepCallouts,
  stepLinks,
  taggedPractice,
} from "./knowledge-graph";
import { inlineCallLayout } from "../call-expansion";

const STORY_NODE_TYPES = [
  "Increment",
  "Epic",
  "SubEpic",
  "Story",
  "Scenario",
  "Background",
  "Step",
  "Example",
  "StoryModel",
];

function graphNode(
  name: string,
  type: string,
  practice = "",
  children: KnowledgeGraphNode[] = [],
): KnowledgeGraphNode {
  const node = new KnowledgeGraphNode();
  node.name = name;
  node.nodeId = `${type}:${name}`;
  node.practice = practice;
  node.nodeType = { name: type } as KnowledgeGraphNode["nodeType"];
  node.children = children;
  return node;
}

function mixedPracticeTree(): KnowledgeGraphNode[] {
  const operation = graphNode("submitFeedback", "Operation", "clean_engineering");
  const step = graphNode("When they send a feedback note", "Step", "stories");
  step.relationships = [{ kind: "invokes", nodeId: operation.nodeId, name: operation.name }];
  return [
    graphNode("domain", "Module", "clean_engineering", [
      graphNode("Customer", "OoadClass", "clean_engineering", [operation]),
      graphNode("customer.ts", "File", "clean_engineering"),
      graphNode("Onboard A Customer", "Story", "stories"),
      graphNode("Given a plan", "Step", "stories"),
      graphNode("Ordering", "BoundedContext", "ddd"),
    ]),
    graphNode("tests", "Package", "stories", [
      graphNode("Select Plan", "Story", "stories", [step]),
      graphNode("select-plan.e2e.ts", "File", "stories"),
    ]),
    graphNode("Customer is known", "Description", "bdd"),
  ];
}

function flatten(nodes: KnowledgeGraphNode[]): KnowledgeGraphNode[] {
  const all: KnowledgeGraphNode[] = [];
  const walk = (items: KnowledgeGraphNode[]) => {
    for (const node of items) {
      all.push(node);
      walk(node.children ?? []);
    }
  };
  walk(nodes);
  return all;
}
import { KnowledgeGraphClient } from "./knowledge-graph-client";

function graph() {
  const loaded = new KnowledgeGraph(null, null, null, null);
  loaded.folder = "/tmp/kg";
  loaded.storyModel.name = "Onboard";
  loaded.storyModel.epics = [{ name: "Onboard" }];
  return loaded;
}

describe("a knowledge graph", () => {
  let subject: KnowledgeGraph;

  beforeEach(() => {
    subject = graph();
  });

  describe("that has been saved", () => {
    it("should write the knowledge graph models", () => {
      subject.saveKnowledgeGraph();
      expect(subject.saved["story-map.kg"]).toContain("Onboard");
    });
  });

  describe("that has been loaded from a presented graph", () => {
    it("should rebuild the nodes from listed_tree", () => {
      const loaded = new KnowledgeGraphClient();
      loaded.takeSave({
        knowledge_graph: { id: "11111111-1111-1111-1111-111111111111", folder: "/tmp/kg" },
        listed_tree: [
          {
            name: "domain",
            node_id: "ce:Module:domain",
            semantic_type: "Module",
            children: [
              {
                name: "customer",
                node_id: "ce:Module:customer",
                semantic_type: "Module",
                children: [
                  { name: "Customer", node_id: "ce:OoadClass:Customer", semantic_type: "OoadClass" },
                ],
              },
            ],
          },
        ],
      });
      expect(loaded.nodes.map((node) => node.name)).toEqual(["domain", "customer", "Customer"]);
      expect(loaded.render()).toContain("domain");
      expect(loaded.render()).toContain('data-kind="Module"');
      expect(loaded.render()).toContain("Customer");
    });

    it("should keep a class under its own folder", () => {
      const loaded = new KnowledgeGraphClient();
      loaded.takeSave({
        knowledge_graph: {
          id: "11111111-1111-1111-1111-111111111111",
          practice_graphs: [
            {
              nodes: [
                {
                  name: "Customer",
                  node_id: "ce:OoadClass:Customer",
                  semantic_type: "OoadClass",
                  practice: "clean_engineering",
                  source: { file: "domain/customer/Customer.ts" },
                },
              ],
            },
          ],
        },
        listed_tree: [
          {
            name: "domain",
            node_id: "ce:Module:domain",
            semantic_type: "Module",
            practice: "clean_engineering",
            children: [
              { name: "customer", node_id: "ce:Module:customer", semantic_type: "Module", children: [] },
            ],
          },
        ],
        filter_options: {
          practices: ["clean_engineering", "ddd"],
          node_types: ["Module", "OoadClass"],
          stages: ["code"],
          relationship_types: ["owns"],
          rules: ["keep-operations-small-focused"],
        },
      });
      const domain = loaded.matching[0];
      expect(domain.children.map((node) => node.name)).toEqual(["customer"]);
      expect(domain.children[0].children.map((node) => node.name)).toContain("Customer");
      expect(loaded.options.practices).toEqual(["clean_engineering", "ddd"]);
      expect(loaded.options.node_types).toContain("OoadClass");
    });

    it("should mark a violation hit as violating and leave the other rule passing", () => {
      const loaded = new KnowledgeGraphClient();
      loaded.takeSave({
        knowledge_graph: {
          id: "22222222-2222-4222-8222-222222222222",
          practice_graphs: [
            {
              nodes: [
                {
                  name: "load",
                  node_id: "ce:Operation:load",
                  semantic_type: "Operation",
                  applicable_rules: ["keep-operations-small-focused"],
                  violations: [],
                  source: { file: "orders/Order.ts" },
                },
                {
                  name: "processEverything",
                  node_id: "ce:Operation:processEverything",
                  semantic_type: "Operation",
                  applicable_rules: ["keep-operations-small-focused"],
                  violations: [{ rule_slug: "keep-operations-small-focused", message: "too big" }],
                  source: { file: "orders/Order.ts" },
                },
              ],
            },
          ],
        },
        listed_tree: [
          { name: "orders", node_id: "ce:Module:orders", semantic_type: "Module", children: [] },
        ],
      });
      const load = loaded.nodes.find((node) => node.name === "load");
      const failing = loaded.nodes.find((node) => node.name === "processEverything");
      expect(load?.ruleHits).toEqual([
        { slug: "keep-operations-small-focused", status: "passing", message: "" },
      ]);
      expect(failing?.ruleHits).toEqual([
        { slug: "keep-operations-small-focused", status: "violating", message: "too big" },
      ]);
    });

    it("should nest classes from practice graphs under their folder", () => {
      const loaded = new KnowledgeGraphClient();
      loaded.takeSave({
        knowledge_graph: {
          id: "11111111-1111-1111-1111-111111111111",
          practice_graphs: [
            {
              nodes: [
                {
                  name: "Customer",
                  node_id: "ce:OoadClass:Customer",
                  semantic_type: "OoadClass",
                  source: { file: "domain/customer/Customer.ts" },
                },
              ],
            },
          ],
        },
        listed_tree: [
          { name: "customer", node_id: "ce:Module:customer", semantic_type: "Module", children: [] },
        ],
      });
            expect(loaded.nodes.map((node) => node.name)).toContain("Customer");
      expect(loaded.render()).toContain("Customer");
    });

    it("should nest a BoundedContext under the folder of the same name", () => {
      const loaded = new KnowledgeGraphClient();
      loaded.takeSave({
        knowledge_graph: {
          id: "11111111-1111-1111-1111-111111111111",
          practice_graphs: [
            {
              nodes: [
                {
                  name: "Customer",
                  node_id: "ddd:BoundedContext:customer",
                  semantic_type: "BoundedContext",
                  source: null,
                  properties: { folder: "" },
                },
              ],
            },
          ],
        },
        listed_tree: [
          {
            name: "customer",
            node_id: "ce:Module:customer",
            semantic_type: "Module",
            children: [],
          },
        ],
      });
      expect(loaded.nodes.map((node) => node.name)).toContain("Customer");
      expect(loaded.render()).toContain("Customer");
    });
  });

  describe("that has been loaded from a path", () => {
    it("should rebuild the nodes from that document", () => {
      subject.saveKnowledgeGraph();
      const loaded = new KnowledgeGraph(null, null, null, null);
      loaded.storyModel.name = "Onboard";
      loaded.loadKnowledgeGraph("/tmp/kg");
      expect(loaded.nodes.map((node) => node.name)).toContain("Onboard");
    });
  });

  describe("that has created a database", () => {
    it("should write master", () => {
      subject.createDatabase();
      expect(subject.master).toContain("master");
    });
    it("should copy master to the working copy", () => {
      subject.createDatabase();
      expect(subject.workingCopy).toContain("working-copy");
    });
  });

  describe("that merges the working copy into master", () => {
    it("should copy the working copy database onto master", () => {
      subject.workingCopy = "/repo/.codeql/javascript-working-copy";
      subject.refreshMaster();
      expect(subject.master).toBe("/repo/.codeql/javascript-working-copy");
      expect(subject.saved["story-map.kg"]).toBeUndefined();
    });
  });

  describe("that reloads the working copy", () => {
    it("should load the latest files into the working copy", () => {
      subject.reloadWorkingCopy();
      expect(subject.workingCopy).toContain("javascript-working-copy");
      expect(subject.loadedLatestFiles).toBe(true);
      expect(subject.saved["story-map.kg"]).toBeUndefined();
    });
  });

  describe("that has updated the working copy", () => {
    describe("with dirty paths", () => {
      it("should be the document that was just saved", () => {
        subject.saveKnowledgeGraph();
        subject.updateWorkingCopy([]);
        expect(subject.saved["story-map.kg"]).toContain("Onboard");
      });
    });
  });

  describe("with selected practices", () => {
    let cascade: KnowledgeGraphFilter;

    beforeEach(() => {
      cascade = new KnowledgeGraphFilter(["Stories"]);
    });

    it("should fill available stages from those practices", () => {
      expect(cascade.stageFilter.choices).toContain("Discovery");
    });

    it("should fill available node types from those practices and stages", () => {
      expect(cascade.nodeFilter.choices).toContain("Story");
    });

    describe("with selected node types", () => {
      beforeEach(() => {
        cascade.nodeFilter.selected = ["OoadClass", "Operation"];
        cascade.relationshipFilter.available(cascade.nodeFilter.selected);
        cascade.ruleFilter.available(cascade.nodeFilter.selected);
      });

      it("should fill available relationships from those nodes", () => {
        expect(cascade.relationshipFilter.choices).toContain("invokes");
      });

      it("should fill available rules from those nodes", () => {
        expect(cascade.ruleFilter.choices).toContain("keep-operations-small-focused");
      });
    });

    describe("with a rule set", () => {
      it("should offer base and project", () => {
        expect(cascade.ruleSetFilter.available).toEqual(["base", "project"]);
      });
    });

    describe("that tags an epic, sub-epic, or story", () => {
      it("should tag them as stories and not as clean engineering or bdd", () => {
        expect(taggedPractice("Epic", "clean_engineering")).toBe("stories");
        expect(taggedPractice("SubEpic", "bdd")).toBe("stories");
        expect(taggedPractice("Story", "clean_engineering")).toBe("stories");
        expect(taggedPractice("OoadClass", "clean_engineering")).toBe("clean_engineering");
        const epic = graphNode("Access Selfcare", "Epic", "clean_engineering");
        const tests = graphNode("tests", "Package", "clean_engineering");
        retagPractice(epic);
        const testsTag = { nodeType: tests.nodeType, practice: tests.practice, properties: { folder: "tests" } };
        retagPractice(testsTag);
        tests.practice = testsTag.practice;
        expect(epic.practice).toBe("stories");
        expect(tests.practice).toBe("stories");
        const included = flatten(retainedTree([tests, epic], ["CleanEngineering"]));
        expect(included.map((node) => node.name)).not.toContain("tests");
        expect(included.map((node) => node.name)).not.toContain("Access Selfcare");
      });
    });

    describe("a story node", () => {
      it("should leave tests, epics, sub-epics, and stories out of clean engineering", () => {
        const epic = graphNode("Access Selfcare", "Epic", "clean_engineering");
        const sub = graphNode("manage-services", "SubEpic", "clean_engineering");
        const story = graphNode("onboard-a-customer", "Story", "clean_engineering");
        expect(isStoryNode(epic)).toBe(true);
        expect(isStoryNode(sub)).toBe(true);
        expect(isStoryNode(story)).toBe(true);
        const tests = graphNode("tests", "Package", "", [
          graphNode("access-selfcare", "Package", "", [epic, graphNode("examples", "Package", "")]),
          graphNode("manage-billing", "Package", "", [graphNode("Manage Billing", "Epic", "stories")]),
          sub,
          story,
        ]);
        expect(isStoryNode(tests)).toBe(true);
        const included = flatten(
          retainedTree(
            [
              graphNode("domain", "Module", "clean_engineering", [
                graphNode("Customer", "OoadClass", "clean_engineering"),
              ]),
              tests,
            ],
            ["CleanEngineering"],
          ),
        );
        const names = included.map((node) => node.name);
        expect(names).toContain("domain");
        expect(names).toContain("Customer");
        expect(names).not.toContain("tests");
        expect(names).not.toContain("access-selfcare");
        expect(names).not.toContain("examples");
        expect(names).not.toContain("manage-billing");
        expect(names).not.toContain("manage-services");
        expect(names).not.toContain("onboard-a-customer");
        const kinds = included.map((node) => node.nodeType?.name);
        expect(kinds).not.toContain("Epic");
        expect(kinds).not.toContain("SubEpic");
        expect(kinds).not.toContain("Story");
      });
    });

    describe("that selects clean engineering", () => {
      it("should leave story nodes out of the folders and files", () => {
        const included = flatten(retainedTree(mixedPracticeTree(), ["CleanEngineering"]));
        const foldersAndFiles = included.filter((node) =>
          ["Module", "Package", "File"].includes(node.nodeType?.name ?? ""),
        );
        expect(foldersAndFiles.map((node) => node.name)).toEqual(["domain", "customer.ts"]);
        for (const node of foldersAndFiles) {
          expect(STORY_NODE_TYPES).not.toContain(node.nodeType?.name);
        }
        for (const node of included) {
          expect(STORY_NODE_TYPES).not.toContain(node.nodeType?.name);
          expect(["Description", "Context", "Observation", "BoundedContext"]).not.toContain(node.nodeType?.name);
        }
        expect(included.map((node) => node.name)).toContain("Customer");
        expect(included.map((node) => node.name)).toContain("submitFeedback");
        expect(included.map((node) => node.name)).not.toContain("When they send a feedback note");
        expect(included.map((node) => node.name)).not.toContain("Onboard A Customer");
        expect(included.map((node) => node.name)).not.toContain("Select Plan");
        expect(included.map((node) => node.name)).not.toContain("Given a plan");
        expect(included.map((node) => node.name)).not.toContain("Customer is known");
        expect(included.map((node) => node.name)).not.toContain("Ordering");
        expect(included.map((node) => node.name)).not.toContain("select-plan.e2e.ts");
      });
    });

    describe("that projects a domain tree", () => {
      it("should keep classes under an aggregate when the folder has a repository", () => {
        const customer = graphNode("Customer", "OoadClass", "clean_engineering", [
          graphNode("load", "Operation", "clean_engineering"),
        ]);
        const repository = graphNode("CustomerRepository", "OoadClass", "clean_engineering");
        const folder = graphNode("customer", "Module", "clean_engineering", [
          customer,
          repository,
          graphNode("customer.ts", "File", "clean_engineering"),
        ]);
        const projected = domainTree([
          graphNode("src", "Module", "clean_engineering", [folder]),
          graphNode("tests", "Package", "stories", [graphNode("Select Plan", "Story", "stories")]),
          graphNode("Customer is known", "Description", "bdd"),
        ]);
        expect(projected.map((node) => node.name)).toEqual(["src"]);
        const aggregate = projected[0].children[0];
        expect(aggregate.nodeType?.name).toBe("Aggregate");
        expect(aggregate.children.map((node) => node.name)).toEqual(["Customer", "CustomerRepository"]);
        expect(aggregate.children[0].nodeType?.name).toBe("EntityRoot");
        expect(aggregate.children[0].children.map((node) => node.name)).toEqual(["load"]);
        expect(aggregate.children[1].nodeType?.name).toBe("Repository");
      });

      it("should leave a folder as a module when it has no root or repository", () => {
        const projected = domainTree([
          graphNode("src", "Module", "", [
            graphNode("notes", "Module", "", [graphNode("Note", "OoadClass", "clean_engineering")]),
          ]),
        ]);
        expect(projected[0].nodeType?.name).toBe("Module");
        expect(projected[0].children[0].nodeType?.name).toBe("Module");
        expect(dddClassKind("Payment <<value object>>")).toBe("ValueObject");
      });
    });

    describe("that selects domain driven design", () => {
      it("should keep clean engineering folders and files and leave story nodes out", () => {
        const included = flatten(retainedTree(mixedPracticeTree(), ["Ddd"]));
        for (const node of included) {
          expect(STORY_NODE_TYPES).not.toContain(node.nodeType?.name);
          expect(["Description", "Context", "Observation"]).not.toContain(node.nodeType?.name);
        }
        expect(included.map((node) => node.name)).toEqual(
          expect.arrayContaining(["domain", "Customer", "customer.ts", "submitFeedback", "Ordering"]),
        );
        expect(included.map((node) => node.nodeType?.name)).toEqual(
          expect.arrayContaining(["OoadClass", "BoundedContext"]),
        );
        expect(included.map((node) => node.name)).not.toContain("Onboard A Customer");
        expect(included.map((node) => node.name)).not.toContain("When they send a feedback note");
        expect(included.map((node) => node.name)).not.toContain("Given a plan");
        expect(included.map((node) => node.name)).not.toContain("Customer is known");
      });
    });

    describe("that selects stories", () => {
      it("should leave class folders and files out", () => {
        const included = flatten(retainedTree(mixedPracticeTree(), ["Stories"]));
        const names = included.map((node) => node.name);
        expect(names).not.toContain("domain");
        expect(names).not.toContain("Customer");
        expect(names).not.toContain("customer.ts");
        expect(names).toContain("Select Plan");
        expect(names).toContain("When they send a feedback note");
        expect(names).not.toContain("submitFeedback");
        expect(names).not.toContain("Ordering");
        expect(names).not.toContain("Customer is known");
        const step = included.find((node) => node.name === "When they send a feedback note");
        expect(step?.relationships.map((link) => link.name)).toContain("submitFeedback");
        for (const node of included) {
          expect(node.practice).not.toBe("clean_engineering");
          expect(node.practice).not.toBe("ddd");
          expect(node.practice).not.toBe("bdd");
        }
      });
    });

    describe("that selects behavior driven development", () => {
      it("should leave story nodes and class folders out", () => {
        const included = flatten(retainedTree(mixedPracticeTree(), ["Bdd"]));
        expect(included.map((node) => node.name)).toEqual(["Customer is known"]);
        for (const node of included) {
          expect(STORY_NODE_TYPES).not.toContain(node.nodeType?.name);
          expect(["Module", "Package", "File", "OoadClass", "Operation", "BoundedContext"]).not.toContain(
            node.nodeType?.name,
          );
        }
      });
    });
  });

  describe("with a chosen node", () => {
    it("should hold that node as selected", () => {
      const node = new KnowledgeGraphNode();
      node.name = "Story";
      node.nodeId = "story";
      subject.nodes = [node];
      subject.matching = [node];
      subject.choose(node);
      expect(subject.selected).toBe(node);
      expect(subject.render()).toContain("is-selected");
    });
  });

  describe("with open branches", () => {
    it("should hold those nodes as expanded", () => {
      const node = new KnowledgeGraphNode();
      node.name = "Epic";
      subject.open(node);
      expect(subject.expanded).toContain(node);
    });

    it("should start closed and restore only branches that were opened", () => {
      expect(subject.expanded).toEqual([]);
      const present = ["practice:clean_engineering", "pkg:domain", "pkg:customer"];
      expect(restoredBranches([], present)).toEqual([]);
      expect(restoredBranches(["pkg:domain"], present)).toEqual(["pkg:domain"]);
      expect(restoredBranches(["pkg:domain", "missing"], present)).toEqual(["pkg:domain"]);
    });

    it("should create the database from scratch and say extraction is in progress", () => {
      expect(databaseBuildRequired("create-database", true)).toBe(true);
      expect(databaseGraphFromScratch("create-database")).toBe(true);
      expect(databaseGraphFromScratch("refresh-master")).toBe(false);
      expect(extractionProgress("Create database", "working", 4)).toBe(
        "Database extraction in progress… 4s",
      );
      const guidance = [
        {
          slug: "honor-every-rule-in-the-artifact",
          practice: "clean_engineering",
          fidelity: "",
          applies_to: ["Operation", "OoadClass"],
        },
        {
          slug: "verb-noun-format",
          practice: "stories",
          fidelity: "story_map",
          applies_to: ["Story"],
        },
        {
          slug: "keep-operations-small-focused",
          practice: "clean_engineering",
          fidelity: "code",
          applies_to: ["Operation"],
        },
      ];
      expect(rulesForFilters(guidance, ["stories"], null, null)).toEqual(["verb-noun-format"]);
      expect(
        rulesForFilters(guidance, ["clean_engineering"], ["implementation"], ["Operation"]),
      ).toEqual(["honor-every-rule-in-the-artifact", "keep-operations-small-focused"]);
      expect(databaseBuildRequired("refresh-master", true)).toBe(true);
      expect(databaseBuildRequired("reload-working-copy", true)).toBe(true);
    });
  });
});

describe("an operation", () => {
  describe("that has source", () => {
    let source: KnowledgeGraphCallSource;

    beforeEach(() => {
      source = new KnowledgeGraphCallSource("placeOrder()\nCart.addItem()", "Cart.ts", 1, 2, "typescript");
      source.source();
    });

    it("should load each call at its line and order", () => {
      expect(source.calls.map((call) => [call.line, call.sequentialOrder, call.operation])).toEqual([
        [1, 1, "placeOrder"],
        [2, 1, "Cart.addItem"],
      ]);
    });

    it("should insert those calls into the text", () => {
      expect(source.text).toContain("call:placeOrder");
    });

    it("should fold each inserted call", () => {
      expect(source.folds.map((fold) => fold.kind)).toEqual(["class", "call"]);
    });
  });

  describe("that calls another class's operation", () => {
    it("should use the call glyph", () => {
      const source = new KnowledgeGraphCallSource("Cart.addItem()", "Order.ts", 1, 1, "typescript");
      source.source();
      expect(source.folds[0].kind).toBe("call");
    });

    it("should fold a call through this to the other operation", () => {
      const source = new KnowledgeGraphCallSource("this.save(customer)", "Customer.ts", 10, 10, "typescript");
      source.source();
      expect(source.calls.map((call) => call.operation)).toEqual(["this.save"]);
      expect(source.folds[0].kind).toBe("call");
    });
  });
});

describe("inlined operation source", () => {
  const members = [
    {
      id: "save",
      name: "save",
      kind: "Operation",
      owner: "CustomerRepository",
      text: "save(customer: Customer): void {\n  store.set(customer)\n}",
      file: "customer.ts",
      start: 20,
      end: 22,
    },
    {
      id: "place",
      name: "placeOrder",
      kind: "Operation",
      owner: "Cart",
      text: "placeOrder(cart: Cart): Receipt {\n  return receipt\n}",
      file: "cart.ts",
      start: 4,
      end: 6,
    },
    {
      id: "customer",
      name: "Customer",
      kind: "OoadClass",
      owner: "",
      text: "class Customer {\n  email: string\n}",
      file: "customer.ts",
      start: 1,
      end: 3,
    },
    {
      id: "receipt",
      name: "Receipt",
      kind: "OoadClass",
      owner: "",
      text: "class Receipt {\n  id: string\n}",
      file: "cart.ts",
      start: 1,
      end: 3,
    },
  ];

  it("inlines an internal call and the parameter and return types", () => {
    const layout = inlineCallLayout(
      "persist(customer: Customer): void {\n  this.save(customer)\n}",
      members,
      "CustomerRepository",
    );
    expect(layout.text).toContain("save(customer: Customer): void {");
    expect(layout.text).toContain("store.set(customer)");
    expect(layout.text).toContain("class Customer {");
    expect(layout.folds.some((fold) => fold.kind === "call")).toBe(true);
    expect(layout.folds.some((fold) => fold.kind === "class")).toBe(true);
  });

  it("inlines a call to an operation on another class", () => {
    const layout = inlineCallLayout(
      "checkout(): Receipt {\n  Cart.placeOrder(cart)\n}",
      members,
      "CustomerRepository",
    );
    expect(layout.text).toContain("placeOrder(cart: Cart): Receipt {");
    expect(layout.text).toContain("class Receipt {");
    expect(layout.folds.some((fold) => fold.kind === "call")).toBe(true);
    expect(layout.folds.some((fold) => fold.kind === "class")).toBe(true);
  });
});

describe("a practice tree", () => {
  it("should root each practice that is not filtered out", () => {
    expect(practiceRootLabels(["clean_engineering"])).toEqual(["Clean Engineering"]);
    expect(practiceRootLabels(["stories"])).toEqual(["Stories"]);
    expect(practiceRootLabels(["ddd"])).toEqual(["Domain Driven Design"]);
    expect(practiceRootLabels(["bdd"])).toEqual(["BDD"]);
    expect(practiceRootLabels([])).toEqual([
      "Clean Engineering",
      "Stories",
      "Domain Driven Design",
      "BDD",
    ]);
  });
});

describe("a source panel", () => {
  it("should shrink when a fold is closed and grow when that fold opens", () => {
    const folds = [new KnowledgeGraphSourceFold(2, 10, "operation")];
    expect(editorHeight(12, folds, [])).toBe(60);
    expect(editorHeight(12, folds, [2])).toBe(240);
  });
});

describe("a scenario step", () => {
    it("should list the fixture examples and the domain operation the test calls", () => {
      const text =
        "subscriber.feedbackSubject = feedbackSubjectExample\nsubscriber.feedbackMessage = feedbackMessageExample\nreceipt = await subscriber.submitFeedback()";
      const members = stepMembers(text);
      expect(members.operations).toEqual(["submitFeedback"]);
      expect(members.examples).toEqual(["feedbackSubjectExample", "feedbackMessageExample"]);
      const layout = stepCallouts(text, [
        { name: "feedbackSubjectExample", text: "feedbackSubjectExample" },
        { name: "feedbackMessageExample", text: "feedbackMessageExample" },
        { name: "submitFeedback", text: "submitFeedback()" },
      ]);
      expect(layout.folds.map((fold) => fold.kind)).toEqual(["call", "call", "call"]);
      expect(layout.text).toContain("    feedbackSubjectExample");
      expect(layout.text).toContain("    submitFeedback()");
    });

    it("should keep the operation a step invokes under that step", () => {
      const operation = graphNode("submitFeedback", "Operation", "clean_engineering");
      const example = graphNode("feedbackSubjectExample", "Example", "stories");
      const step = graphNode("When they send a feedback note", "Step", "stories", [operation, example]);
      step.relationships = [
        { kind: "invokes", nodeId: operation.nodeId, name: operation.name },
        { kind: "demonstrates", nodeId: example.nodeId, name: example.name },
      ];
      const included = flatten(retainedTree([step], ["Stories"]));
      expect(included.map((node) => node.name)).toContain("submitFeedback");
      expect(included.map((node) => node.name)).toContain("feedbackSubjectExample");
      const engineering = flatten(retainedTree([step], ["CleanEngineering"]));
      expect(engineering.map((node) => node.name)).not.toContain("When they send a feedback note");
    });

    it("should leave belongsTo out of the relationship list", () => {
      expect(
        shownRelationships([
          { kind: "belongsTo", nodeId: "story", name: "Load Customer" },
          { kind: "invokes", nodeId: "load", name: "load" },
        ]),
      ).toEqual([{ kind: "invokes", nodeId: "load", name: "load" }]);
    });

    it("should link an invoked operation, a demonstrated example class, and an expected class", () => {
      const operations = [{ id: "load", name: "load", owner: "CustomerRepository" }];
      const examples = [{ name: "seedCustomerWithAddress", classes: ["Customer"] }];
      const classes = ["Customer", "Onboarding"];
      expect(
        stepLinks("customer = await ctx.customerRepository.load(accountCredentials);", operations, examples, classes)
          .invokes,
      ).toEqual(["load"]);
      expect(
        stepLinks(
          "customer = seedCustomerWithAddress(ctx.customerRepository, accountCredentials);",
          operations,
          examples,
          classes,
        ).examples,
      ).toEqual([{ name: "seedCustomerWithAddress", classes: ["Customer"] }]);
      expect(
        stepLinks(
          "expect(customer).toBeInstanceOf(Customer)\nexpect(customer.onboarding).toBeInstanceOf(Onboarding)",
          operations,
          examples,
          classes,
        ).expected,
      ).toEqual(["Customer", "Onboarding"]);
      const customer = graphNode("Customer", "OoadClass", "clean_engineering");
      const thenStep = graphNode("Then the result is a customer", "Step", "stories", [customer]);
      thenStep.relationships = [{ kind: "expected", nodeId: customer.nodeId, name: customer.name }];
      expect(flatten(retainedTree([thenStep], ["Stories"])).map((node) => node.name)).toContain("Customer");
    });
});

describe("a property", () => {
  describe("that has source", () => {
    it("behaves like an operation that has source", () => {
      const source = new KnowledgeGraphCallSource("total()\n", "Cart.ts", 1, 1, "typescript");
      source.source();
      expect(source.calls[0].operation).toBe("total");
    });
  });
});
