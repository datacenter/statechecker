import {ManagedObject} from "./managed-object";

export class DefinitionList {
  count: number;
  objects: Definition[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class Definition {
  definition: string;
  description: string;
  managed_objects: ManagedObject[]
}
