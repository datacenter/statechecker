import {Component, OnInit} from "@angular/core";
import {Router} from "@angular/router";
import {BackendService} from "../_service/backend.service";
import {HttpErrorResponse} from "@angular/common/http";
import {NotificationsService} from "angular2-notifications";
import {Version} from "../_model/version";

@Component({
  templateUrl: './login.component.html',
})

export class LoginComponent implements OnInit {
  loading: boolean;
  username: string;
  password: string;
  version: Version;

  constructor(public router: Router, private backendService: BackendService, private notificationService: NotificationsService) {
  }

  ngOnInit(): void {
    this.backendService.getVersion().subscribe((results) => {
      this.version = results;
    });
  }

  public onSubmit() {
    this.loading = true;
    this.backendService.login(this.username, this.password).subscribe((results) => {
      this.loading = false;
      localStorage.setItem('isLoggedIn', 'true');
      localStorage.setItem('userName', this.username);
      this.backendService.getUserDetails(this.username).subscribe((response) => {
        const userDetails = response['objects'][0];
        localStorage.setItem('userRole', userDetails['role']);
      }, (error) => {
        this.notificationService.error('Could not get user details');
      });
      this.router.navigate(['/']);
    }, (err) => {
      this.loading = false;
      if (err instanceof HttpErrorResponse && err.status === 401) {
        localStorage.removeItem('isLoggedIn');
        this.notificationService.error('Error', 'Authentication failed');
      } else {
        this.notificationService.error('Error', err.statusText);
      }
    });
  }
}
