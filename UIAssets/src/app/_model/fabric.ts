export class FabricList {
  count: number;
  objects: Fabric[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class Fabric {
  apic_cert: string;
  apic_hostname: string;
  apic_username: string;
  apic_password: string;
  controllers: string[];
  fabric: string;

  constructor(apic_cert?: string, apic_hostname?: string, apic_username?: string, apic_password?: string, controllers?: string[], fabric?: string) {
    this.apic_cert = apic_cert;
    this.apic_hostname = apic_hostname;
    this.apic_username = apic_username;
    this.apic_password = apic_password;
    this.controllers = controllers;
    this.fabric = fabric;
  }
}
