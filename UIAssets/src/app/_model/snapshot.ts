import {Fabric} from "./fabric";

export class SnapshotList {
  count: number;
  objects: Snapshot[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class Snapshot {
  _id: string;
  definition: string;
  description: string;
  error: string;
  fabric: string;
  fabric_domain: string;
  filename: string;
  filesize: number;
  nodes: number[];
  objects: number;
  progress: number;
  start_time: number;
  status: string;
  total_time: number;
  wait_time: number;
  fabric_obj: Fabric;

  public constructor(fabric: Fabric, description: string = '', definition: string = 'default') {
    this.description = description;
    this.fabric_obj = fabric;
    this.fabric = fabric.fabric;
    this.definition = definition;
  }
}
