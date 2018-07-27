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

  public constructor(fabric?: string, apic_cert?: string, apic_hostname?: string, apic_username?: string, apic_password?: string) {
    this.fabric = fabric;
    this.apic_cert = apic_cert;
    this.apic_hostname = apic_hostname;
    this.apic_username = apic_username;
    this.apic_password = apic_password;
  }
}
