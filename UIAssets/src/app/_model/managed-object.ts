export class ManagedObjectList {
  count: number;
  objects: ManagedObject[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

class Attribute {
  labels: string[];
  name: string;
  remap: string[];
  severity: string
}

export class ManagedObject {
  analyzer: string;
  attributes: Attribute[];
  classname: string;
  description: string;
  classnames: string[];
  definition: string;
  exclude: string[];
  include: string[];
  key: string;
  labels: string[];
  name: string;
  remap: string[];
  severity: string;
  uri: string;
}
