import { describe, it } from "vitest";

describe("a story map", () => {
  describe("from a channel", () => {
    describe("to knowledge graph", () => {
      it("behaves like a story map saved through a channel", () => {
        // BDD: SIGNATURE
      });
    });
  });
});


import { describe, it } from "vitest";

describe("a class model", () => {
  describe("from a channel", () => {
    describe("to knowledge graph", () => {
      it("behaves like a class model saved through a channel", () => {
        // BDD: SIGNATURE
      });
    });
  });
});


import { describe, it } from "vitest";

describe("a domain driven design model", () => {
  describe("from a channel", () => {
    describe("to knowledge graph", () => {
      it("behaves like a domain driven design model saved through a channel", () => {
        // BDD: SIGNATURE
      });
    });
  });
});


import { describe, it } from "vitest";

describe("a knowledge graph", () => {
  describe("that has been saved", () => {
    it("should write the knowledge graph models", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that has been loaded from a path", () => {
    it("should rebuild the nodes from that document", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that has created a database", () => {
    it("should write master", () => {
      // BDD: SIGNATURE
    });
    it("should copy master to the working copy", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that has refreshed the master", () => {
    it("should be the document that was just saved", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that has reloaded the working copy", () => {
    it("should be the document that was just saved", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that has updated the working copy", () => {
    describe("with dirty paths", () => {
      it("should be the document that was just saved", () => {
        // BDD: SIGNATURE
      });
    });
  });
  describe("with selected practices", () => {
    it("should fill available stages from those practices", () => {
      // BDD: SIGNATURE
    });
    it("should fill available node types from those practices and stages", () => {
      // BDD: SIGNATURE
    });
    describe("with selected node types", () => {
      it("should fill available relationships from those nodes", () => {
        // BDD: SIGNATURE
      });
      it("should fill available rules from those nodes", () => {
        // BDD: SIGNATURE
      });
    });
    describe("with a rule set", () => {
      it("should offer base and project", () => {
        // BDD: SIGNATURE
      });
    });
  });
  describe("with a chosen node", () => {
    it("should hold that node as selected", () => {
      // BDD: SIGNATURE
    });
  });
  describe("with open branches", () => {
    it("should hold those nodes as expanded", () => {
      // BDD: SIGNATURE
    });
  });
});


import { describe, it } from "vitest";

describe("an operation", () => {
  describe("that has source", () => {
    it("should load each call at its line and order", () => {
      // BDD: SIGNATURE
    });
    it("should insert those calls into the text", () => {
      // BDD: SIGNATURE
    });
    it("should fold each inserted call", () => {
      // BDD: SIGNATURE
    });
  });
  describe("that calls another class's operation", () => {
    it("should use the call glyph", () => {
      // BDD: SIGNATURE
    });
  });
});


import { describe, it } from "vitest";

describe("a property", () => {
  describe("that has source", () => {
    it("behaves like an operation that has source", () => {
      // BDD: SIGNATURE
    });
  });
});
