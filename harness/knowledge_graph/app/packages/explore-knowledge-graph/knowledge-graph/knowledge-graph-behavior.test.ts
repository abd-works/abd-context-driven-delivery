import { describe, it, expect, beforeEach } from "vitest";
import {
  KnowledgeGraph,
  KnowledgeGraphCallSource,
  KnowledgeGraphFilter,
  KnowledgeGraphNode,
} from "./knowledge-graph";

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
  });

  describe("with a chosen node", () => {
    it("should hold that node as selected", () => {
      const node = new KnowledgeGraphNode();
      node.name = "Story";
      subject.choose(node);
      expect(subject.selected).toBe(node);
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

describe("a property", () => {
  describe("that has source", () => {
    it("behaves like an operation that has source", () => {
      const source = new KnowledgeGraphCallSource("total()\n", "Cart.ts", 1, 1, "typescript");
      source.source();
      expect(source.calls[0].operation).toBe("total");
    });
  });
});
