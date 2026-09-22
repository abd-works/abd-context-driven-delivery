/**
 * TypeScript copies of practice node types so CodeQL javascript
 * populate can bind Stories, Clean Engineering, DDD, BDD, and UX
 * onto GraphNode the same way the Python model does.
 *
 * Sources: harness/knowledge_graph/model/nodes.py,
 * knowledge-graph-sketch.md practice node families.
 */
import { GraphNode, type NodeDto } from './knowledge-graph';

export class Module extends GraphNode {}
export class OoadClass extends GraphNode {}
export class Property extends GraphNode {}
export class Operation extends GraphNode {}
export class BoundedContext extends Module {}
export class Aggregate extends Module {}
export class Entity extends OoadClass {}
export class EntityRoot extends Entity {}
export class Repository extends OoadClass {}
export class ValueObject extends OoadClass {}
export class Epic extends GraphNode {}
export class SubEpic extends Epic {}
export class Story extends GraphNode {}
export class Scenario extends GraphNode {}
export class Step extends GraphNode {}
export class Example extends GraphNode {}
export class Description extends GraphNode {}
export class Context extends GraphNode {}
export class Observation extends GraphNode {}
export class Screen extends GraphNode {}
export class Control extends GraphNode {}

const PRACTICE_TYPES: Record<string, new (dto: NodeDto) => GraphNode> = {
  Module,
  OoadClass,
  Property,
  Operation,
  BoundedContext,
  Aggregate,
  Entity,
  EntityRoot,
  Repository,
  ValueObject,
  Epic,
  SubEpic,
  Story,
  Scenario,
  Step,
  Example,
  Description,
  Context,
  Observation,
  Screen,
  Control,
};

export function practiceNodeFromDto(dto: NodeDto): GraphNode {
  const Type = PRACTICE_TYPES[dto.semantic_type] ?? GraphNode;
  return new Type(dto);
}
