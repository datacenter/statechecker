export class UserList {
  count: number;
  objects: User[];

  public constructor() {
    this.count = 0;
    this.objects = [];
  }
}

export class User {
  username: string;
  role: any;
  last_login: number;

  public constructor() {
  }
}
