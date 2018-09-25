import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {environment} from '../../environments/environment';


@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html'
})

export class WelcomeComponent implements OnInit {
  app_mode = environment.app_mode;

  constructor(public router: Router) {
  }

  ngOnInit() {
  }

  goToFabric() {
    this.router.navigate(['fabrics']);
  }

  goToSnapshot() {
    this.router.navigate(['snapshots']);
  }

  goToComparison() {
    this.router.navigate(['comparisons']);
  }

}
