export class ComparisonResultList {
  count: number;
  objects: ComparisonResult[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class ModifiedComparisonResult {
  key1: string;
  key2: string;
  map_key: string;
  modified: [{
    attribute: string,
    map_value1: string,
    map_value2: string,
    value1: string,
    value2: string
  }]
}

export class ComparisonResult {
  _id: string;
  classname: string;
  compare_id: string;
  equal: string[];
  created: string[];
  deleted: string[];
  modified: ModifiedComparisonResult[];
  name: string;
  node_id: number;
  total: {
    created: number;
    deleted: number;
    equal: number;
    modified: number;
    s1: number;
    s2: number
  }
}
