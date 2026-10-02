import { describe, it, expect, beforeEach } from "vitest";
import {
  KnowledgeGraph,
  KnowledgeGraphCallSource,
  KnowledgeGraphFilter,
  KnowledgeGraphNode,
  KnowledgeGraphSourceFold,
  editorHeight,
  practiceRootLabels,
  stepMembers,
} from "./knowledge-graph";
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

  describe("that has refreshed the master", () => {
    it("should be the document that was just saved", () => {
      subject.saveKnowledgeGraph();
      subject.refreshMaster();
      expect(subject.saved["story-map.kg"]).toContain("Onboard");
    });
  });

  describe("that has reloaded the working copy", () => {
    it("should be the document that was just saved", () => {
      subject.saveKnowledgeGraph();
      subject.reloadWorkingCopy();
      expect(subject.saved["story-map.kg"]).toContain("Onboard");
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

    describe("that selects clean engineering", () => {
      it("should leave stories and domain driven design out of the class model", () => {
        const filter = new KnowledgeGraphFilter(["CleanEngineering"]);
        expect(filter.nodeFilter.choices).toContain("OoadClass");
        expect(filter.nodeFilter.choices).not.toContain("Story");
        expect(filter.nodeFilter.choices).not.toContain("BoundedContext");
        expect(filter.nodeFilter.choices).not.toContain("Description");
      });
    });

    describe("that selects domain driven design", () => {
      it("should include clean engineering plus domain driven design stereotypes", () => {
        const filter = new KnowledgeGraphFilter(["Ddd"]);
        expect(filter.nodeFilter.choices).toContain("BoundedContext");
        expect(filter.nodeFilter.choices).toContain("OoadClass");
        expect(filter.nodeFilter.choices).toContain("Module");
        expect(filter.nodeFilter.choices).not.toContain("Story");
        expect(filter.nodeFilter.choices).not.toContain("Description");
      });
    });

    describe("that selects behavior driven development", () => {
      it("should leave stories and clean engineering out", () => {
        const filter = new KnowledgeGraphFilter(["Bdd"]);
        expect(filter.nodeFilter.choices).toContain("Observation");
        expect(filter.nodeFilter.choices).not.toContain("Story");
        expect(filter.nodeFilter.choices).not.toContain("OoadClass");
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
    const members = stepMembers(
      "subscriber.feedbackSubject = feedbackSubjectExample\nsubscriber.feedbackMessage = feedbackMessageExample\nreceipt = await subscriber.submitFeedback()",
    );
    expect(members.operations).toEqual(["submitFeedback"]);
    expect(members.examples).toEqual(["feedbackSubjectExample", "feedbackMessageExample"]);
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
