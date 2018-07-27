import {Injectable} from '@angular/core';
import {CanActivate, Router} from '@angular/router';
import {environment} from "../../environments/environment";

@Injectable()
export class AuthGuardService implements CanActivate {

  constructor(public router: Router) {
  }

  canActivate(): boolean {
    if (localStorage.getItem('isLoggedIn') != 'true' && environment.login_required) {
      this.router.navigate(['login']);
      return false;
    } else {
      return true;
    }
  }
}
