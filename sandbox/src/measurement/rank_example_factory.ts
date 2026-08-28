/**
 * # @toolset-manifest python -m tools manifest context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
 * # invoke-edit: action satisfy | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 * # invoke-check: action validate | toolset: context_tools.clean_engineering.clean_engineering:CleanEngineering
 */

import { Rank } from "./rank.js";

const examples = {
  rankFive: { value: 5 },
};

// interface IRankExampleFactory
export class IRankExampleFactory {
  loadRankFive() {}
}

// implements IRankExampleFactory
export class RankExampleFactory {
  /**
   * Fake: mock/stub framework creates IRank; feed examples.
   * Isolated: new Rank(...ctor-injected mocks/stubs...).
   * Production: new Rank(...real collaborators...).
   */
  loadRankFive({ mode } = { mode: "fake" }) {
    // examples[rankFive] -> IRank
    const bundle = examples.rankFive;

    if (mode === "fake") {
      const rank = {
        get value() {
          return bundle.value;
        },
        get measurementsTable() {
          return null;
        },
        toMeasure(dimension) {
          return { amount: `rank ${bundle.value} ${dimension}`, dimension };
        },
        distanceFrom(timeRank, speedRank) {
          return {
            get value() {
              return Number(timeRank.value) + Number(speedRank.value);
            },
          };
        },
        timeFrom(distanceRank, speedRank) {
          return {
            get value() {
              return Number(distanceRank.value) - Number(speedRank.value);
            },
          };
        },
        throwDistance(strengthRank, massRank) {
          return {
            get value() {
              return Number(strengthRank.value) - Number(massRank.value);
            },
          };
        },
      };
      return { rank, ...bundle };
    }

    if (mode === "isolated") {
      const measurementsTable = {
        lookup(rank, dimension) {
          return { amount: `rank ${rank.value} ${dimension}`, dimension };
        },
      };
      return { rank: new Rank(bundle.value, measurementsTable), ...bundle };
    }

    const measurementsTable = {
      lookup(rank, dimension) {
        return { amount: `rank ${rank.value} ${dimension}`, dimension };
      },
    };
    return { rank: new Rank(bundle.value, measurementsTable), ...bundle };
  }
}
