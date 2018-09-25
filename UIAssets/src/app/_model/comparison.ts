import {Snapshot} from "./snapshot";

export class ComparisonList {
  count: number;
  objects: Comparison[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class ComparisonTotal {
  'created': number;
  'deleted': number;
  'modified': number;
  'equal': number;
}

export class NodeComparisonTotal {
  'created': number;
  'deleted': number;
  'modified': number;
  'equal': number;
  'node_id': number;
}

export class ClassComparisonTotal {
  'created': number;
  'deleted': number;
  'modified': number;
  'equal': number;
  'classname': string;
  'name': string;
}

export class Comparison {
  _id: string;
  classnames: string[];
  definition: string;
  dynamic: boolean;
  error: string;
  nodes: string[];
  progress: number;
  remap: boolean;
  serialize: boolean;
  severity: string;
  snapshot1: string;
  snapshot2: string;
  start_time: number;
  statistic: boolean;
  status: string;
  timestamp: boolean;
  total_time: number;
  total: ComparisonTotal;
  total_per_class: ClassComparisonTotal[];
  total_per_node: NodeComparisonTotal[];
  snapshot1_obj: Snapshot;
  snapshot2_obj: Snapshot;

  public constructor(snapshot1?: Snapshot, snapshot2?: Snapshot) {
    if (snapshot1) {
      this.snapshot1_obj = snapshot1;
      this.snapshot1 = snapshot1._id;
    }
    if (snapshot2) {
      this.snapshot2_obj = snapshot2;
      this.snapshot2 = snapshot2._id;
    }
    this.remap = true;
    this.serialize = false;
    this.severity = 'info';
  }

}
